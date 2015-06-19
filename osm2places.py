#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import os
import sys
import urlparse
import json

try:
    from requests_oauthlib import OAuth1Session
except ImportError:
    OAuth1Session = None
    print("requests_oauthlib is needed.  Add it to your system with:")
    if os == 'nt':
        print("c:\python27\ArcGIS10.3\Scripts\pip install requests_oauthlib")
    else:
        print("sudo easy_install pip (if you do not have pip)")
        print("sudo pip install requests_oauthlib")
    sys.exit()
import requests

# Before accessing resources you will need to obtain a few credentials from
# your provider (i.e. OSM) and authorization from the user for whom you wish
# to retrieve resources for.
from secrets import *


def setup(site, options=None):
    url = secrets[site]['url']
    client_token = secrets[site]['consumer_key']
    client_secret = secrets[site]['consumer_secret']

    # Get Request Tokens
    request_url = url + '/oauth/request_token'
    if options and options.verbose:
        print "Getting Request Tokens from", request_url
        print "Client Token", client_token
        print "Client Secret", client_secret
    res = requests.post(request_url, None)
    if res.status_code != 200:
        return 'Request Error', res.status_code, res.text

    request_tokens = simplifydict(urlparse.parse_qs(res.text))
    if options and options.verbose:
        print "Request Token", request_tokens['oauth_token']
        print "Request Secret", request_tokens['oauth_token_secret']

    # Authorize User
    if options and options.verbose:
        print "Authorizing user"
    auth_url = url + '/oauth/add_active_directory_user'
    error, userid, username = getuseridentity(site, request_tokens, options)
    if error:
        return error, userid, username
    auth_data = {
        'query': request_tokens,
        'userId': userid,
        'name': username
    }
    header = {
        'Content-type': 'application/json',
        'Accept': 'text/plain'
    }
    # Ignore the response (display name)
    res = requests.post(auth_url, data=json.dumps(auth_data), headers=header)
    if res.status_code != 200:
        return 'Authorization Error', res.status_code, res.text
    if options and options.verbose:
        print "Authorized user", res.text

    # Get Access Tokens
    access_url = url + '/oauth/access_token'
    if options and options.verbose:
        print "Getting Access Tokens from", access_url
    auth = ('OAuth ' +
            'oauth_token="' + request_tokens['oauth_token'] + '", ' +
            'oauth_token_secret="' + request_tokens['oauth_token_secret'] + '"')
    header = {'authorization': auth}
    res = requests.request('post', url=access_url, headers=header)
    if res.status_code != 200:
        return 'Access Error', res.status_code, res.text

    access_tokens = simplifydict(urlparse.parse_qs(res.text))
    if options and options.verbose:
        print "Access Token", access_tokens['oauth_token']
        print "Access Secret", access_tokens['oauth_token_secret']

    # Initialize the Oauth object to create signed requests
    oauth = OAuth1Session(client_token,
                          client_secret=client_secret,
                          resource_owner_key=access_tokens['oauth_token'],
                          resource_owner_secret=access_tokens[
                              'oauth_token_secret'])
    return None, url, oauth


# noinspection PyUnusedLocal
def getuseridentity(site, request_tokens, options=None):
    if options and options.username:
        username = options.username
    else:
        username = os.getenv('USERNAME')
    if not username:
        return 'User Error', 0, 'No user given'

    if options and options.verbose:
        print "Looking up id for user", username

    req = 'http://insidemaps.nps.gov/user/lookup?query=' + username
    res = requests.get(req)
    if res.status_code != 200:
        return 'User Error', res.status_code, res.text
    data = json.loads(res.text)
    if len(data) < 1:
        return 'User Error', 200, 'User not found'
    try:
        userid = data[0]['userId']
        displayname = data[0]['firstName'] + ' ' + data[0]['lastName']
    except KeyError:
        return 'User Error', 200, 'Unexpected response from user lookup'
    if options and options.verbose:
        print "Found id", userid
    return None, userid, displayname


def simplifydict(dictoflists):
    """
    urlparse.parse_qs returns a dict where each value is a list with
     only one item.  This simplifies those lists.
    """
    newdict = {}
    for key in dictoflists:
        item = dictoflists[key]
        if item and type(item) is list and len(item) == 1:
            newdict[key] = item[0]
        else:
            newdict[key] = item
    return newdict


def openchangeset(oauth, root, options=None):
    # return Error (str), Changeset Id (str)
    if options and options.verbose:
        print 'Create change set'
    osm_changeset_payload = ('<osm><changeset>'
                             '<tag k="created_by" v="arc2places"/>'
                             '<tag k="comment" v="upload of OsmChange file"/>'
                             '</changeset></osm>')
    try:
        resp = oauth.put(root + '/api/0.6/changeset/create',
                         data=osm_changeset_payload,
                         headers={'Content-Type': 'text/xml'})
    except requests.exceptions.ConnectionError:
        return "Unable to Connect to " + root, None
    if resp.status_code != 200:
        baseerror = "Failed to open changeset. Status: {0}, Response: {0}"
        error = baseerror.format(resp.status_code, resp.text)
        return error, None
    else:
        cid = resp.text
    if options and options.verbose:
        print "Created change set", cid
    return None, cid


def uploadchangeset(oauth, root, cid, change, options=None):
    # return Error (str), Upload Response (str)
    path = root + '/api/0.6/changeset/' + cid + '/upload'
    if options and options.verbose:
        print 'Upload to change set', cid
    resp = oauth.post(path, data=change, headers={'Content-Type': 'text/xml'})
    if resp.status_code != 200:
        baseerror = "Failed to upload changeset. Status: {0}, Response: {0}"
        error = baseerror.format(resp.status_code, resp.text)
        return error, None
    else:
        data = resp.text
        if options and options.verbose:
            print "Uploaded change set successfully"
            # print "response",data
    return None, data


def closechangeset(oauth, root, cid, options=None):
    if options and options.verbose:
        print "Close change set", cid
    oauth.put(root + '/api/0.6/changeset/' + cid + '/close')
    if options and options.verbose:
        print "Closed change set successfully"


def fixchangefile(cid, data):
    i = 'changeset="-1"'
    o = 'changeset="' + cid + '"'
    return data.replace(i, o)


def makeidmap(idxml, uploaddata, options=None):
    if options and options.verbose:
        print "Process response"
    placesids = {}
    root = Et.fromstring(idxml)
    if root.tag != "diffResult":
        return "Response is not a diffResult", None
    for child in root:
        placesids[child.attrib['old_id']] = child.attrib['new_id']
    gisids = {}
    root = Et.fromstring(uploaddata)
    # this must be a valid osmChange file,
    # or we wouldn't get this far, so proceed
    for child in root[0]:
        tempid = child.attrib['id']
        for tag in child.findall('tag'):
            if tag.attrib['k'] == 'nps:source_id':
                gisids[tempid] = tag.attrib['v']
    resp = "PlaceId,GEOMETRYID\n"
    for tempid in gisids:
        resp += placesids[tempid] + "," + gisids[tempid] + "\n"
    if options and options.verbose:
        print "Processed response"
    return None, resp


def upload_bytes(data, options=None, server=None, user=None):
    """
    Writes input as an OsmChange file to the server as the oauth user

    :rtype : (str, bytes)
    :param data: bytes as from open(name, 'rb').read() containing the upload
    :param server: string - url of OSM API 0.6 server.
    :param options: an object of type DefaultOptions for setting behavior options
    :param user: oauth object representing the credentials of the current user
    :return: tuple of an error as string, and data as bytes suitable for input
             to open(name, 'wb').write().  The error or the data is None
    """
    if not user:
        error, server, user = setup('places', options)
        if error:
            return str(error) + ' ' + str(server) + ' ' + str(user), None
    error, cid = openchangeset(user, server, options)
    if cid:
        error, resp = uploadchangeset(user, server, cid,
                                      fixchangefile(cid, data), options)
        closechangeset(user, server, cid, options)
        if resp:
            error, idmap = makeidmap(resp, data, options)
            if idmap:
                return None, idmap
            return "Failed to relate Places and GIS date " + error, None
        return "Server did not return and results. " + error, None
    return "Unable to open a changeset, check the permissions. " + error, None


def upload(readpath, writepath, options=None, root=None, oauth=None):
    """
    Uploads an OsmChange file and saves the results in a file.

    The OsmChange file is send to the server at root as the oauth user.

    :rtype : str
    :param readpath: string - file system path of OsmChange to upload
    :param writepath: string - file system path to create with response
    :param options: an object of type DefaultOptions for setting behavior options
    :param root: string - base url of OSM API 0.6 server.
    :param oauth: oauth object representing the credentials of the current user
    :return: error message or None on success
    """
    with open(readpath, 'rb') as fr:
        error, data = upload_bytes(fr.read(), options, root, oauth)
        if error:
            return error
        with open(writepath, 'wb') as fw:
            fw.write(data)


class DefaultOptions:
    username = None
    verbose = False


def test():
    opts = DefaultOptions()
    opts.verbose = True
    error, url, tokens = setup('places', opts)
    if error:
        print str(error) + ' ' + str(url) + ' ' + str(tokens)
        return

    error = upload('./tests/test_Parking.osm', './tests/test_parking_pids.csv', opts, url,
                   tokens)
    if error:
        print error
    else:
        print "Done."


def cmdline():
    # Setup program usage
    usage = """%prog SRC DST
    or:    %prog --help

    Uploads SRC to Places and saves the response in DST
    SRC is an OsmChange file
    DST is a CSV file that relates the GIS ids in the change file
    to the id numbers assigned in Places."""

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-u", "--username", dest="username", type=str, help=(
        "Domain user logon name. " +
        "Defaults to None. When None, will load from " +
        "'username' environment variable."), default=None)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true")
    parser.set_defaults(verbose=False)

    # Parse and process arguments
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error(u"You must specify a source and destination")
    elif len(args) > 2:
        parser.error(u"You have specified too many arguments.")

    # Input and output file
    srcfile = args[0]
    dstfile = args[1]
    if not os.path.exists(srcfile):
        parser.error(u"The input file does not exist.")
    if os.path.exists(dstfile):
        parser.error(u"The destination file exist.")
    error = upload(srcfile, dstfile, options)
    if error:
        print error
    else:
        print "Upload successful."


if __name__ == '__main__':
    test()
    # cmdline()
