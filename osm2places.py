# requests_oauthlib is needed
# sudo easy_install pip
# sudo pip install requests requests_oauthlib
# on windows:
#   c:\python27\ArcGIS10.3\Scripts\pip install requests_oauthlib

from requests_oauthlib import OAuth1Session
import xml.etree.ElementTree as ET

# Before accessing resources you will need to obtain a few credentials from
# your provider (i.e. OSM) and authorization from the user for whom you wish
# to retrieve resources for.
from secrets import *


def setup(site):
    url = secrets[site]['url']
    client_token = secrets[site]['consumer_key']
    client_secret = secrets[site]['consumer_secret']
    access_token = secrets[site]['token']
    access_secret = secrets[site]['token_secret']
    if not access_secret:
        # get request token
        request_url = url + '/oauth/request_token'
        oauth = OAuth1Session(client_token, client_secret=client_secret)
        fetch_response = oauth.fetch_request_token(request_url)
        request_token = fetch_response['oauth_token']
        request_secret = fetch_response['oauth_token_secret']

        # authorize
        verifier = secrets[site]['verifier']
        oauth = OAuth1Session(client_token,
                              client_secret=client_secret,
                              resource_owner_key=request_token,
                              resource_owner_secret=request_secret,
                              verifier=verifier)

        # get access tokens
        access_url = url + '/oauth/access_token'
        fetch_response = oauth.fetch_access_token(access_url)
        access_token = fetch_response['oauth_token']
        access_secret = fetch_response['oauth_token_secret']

        # cache access_tokens

    oauth = OAuth1Session(client_token,
                          client_secret=client_secret,
                          resource_owner_key=access_token,
                          resource_owner_secret=access_secret)
    return url, oauth


def openchangeset(oauth, root):
    # return Error (str), Changeset Id (str)
    osm_changeset_payload = ('<osm><changeset>'
                             '<tag k="created_by" v="arc2places"/>'
                             '<tag k="comment" v="upload of OsmChange file"/>'
                             '</changeset></osm>')
    resp = oauth.put(root+'/api/0.6/changeset/create',
                     data=osm_changeset_payload,
                     headers={'Content-Type': 'text/xml'})
    if resp.status_code != 200:
        baseerror = "Failed to open changeset. Status: {0}, Response: {0}"
        error = baseerror.format(resp.status_code, resp.text)
        return error, None
    else:
        cid = resp.text
        # print "Opened Changeset #", cid
    return None, cid


def uploadchangeset(oauth, root, cid, change):
    path = root+'/api/0.6/changeset/' + cid + '/upload'
    print 'POST', path
    resp = oauth.post(path, data=change, headers={'Content-Type': 'text/xml'})
    if resp.status_code != 200:
        baseerror = "Failed to upload changeset. Status: {0}, Response: {0}"
        error = baseerror.format(resp.status_code, resp.text)
        return error, None
    else:
        data = resp.text
        # print "Uploaded Changeset #", cid
        # print "response",data
    return None, data


def closechangeset(oauth, root, cid):
    oauth.put(root+'/api/0.6/changeset/' + cid + '/close')
    # print 'Closed Changeset #', cid


def fixchangefile(cid, data):
    i = 'changeset="-1"'
    o = 'changeset="' + cid + '"'
    return data.replace(i, o)


def makeidmap(idxml, uploadfile):
    placesids = {}
    root = ET.fromstring(idxml)
    if root.tag != "diffResult":
        return "Response is not a diffResult", None
    for child in root:
        placesids[child.attrib['old_id']] = child.attrib['new_id']
    gisids = {}
    root = ET.parse(uploadfile).getroot()
    # this must be a valid osmChange file,
    # or we wouldn't get this far, so proceed
    for child in root[0]:
        tempid = child.attrib['id']
        for tag in child:
            if tag.attrib['k'] == 'nps:source_id':
                gisids[tempid] = tag.attrib['v']
    resp = "PlaceId,GEOMETRYID\n"
    for tempid in gisids:
        resp += placesids[tempid] + "," + gisids[tempid] + "\n"
    return None, resp


def upload_bytes(data, server=None, user=None):
    """
    Writes input as an OsmChange file to the server as the oauth user

    :rtype : (str, bytes)
    :param data: bytes as from open(name, 'rb').read() containing the upload
    :param server: string - url of OSM API 0.6 server.
    :param user: oauth object representing the credentials of the current user
    :return: tuple of an error as string, and data as bytes suitable for input
             to open(name, 'wb').write().  The error or the data is None
    """
    if not user:
        server, user = setup('local')
    error, cid = openchangeset(user, server)
    if cid:
        error, resp = uploadchangeset(user, server, cid,
                                      fixchangefile(cid, data))
        closechangeset(user, server, cid)
        if resp:
            error, idmap = makeidmap(resp, data)
            if idmap:
                return None, idmap
            return "Failed to relate Places and GIS date " + error, None
        return "Server did not return and results. " + error, None
    return "Unable to open a changeset, check the permissions. " + error, None


def upload(readpath, writepath, root=None, oauth=None):
    """
    Uploads an OsmChange file and saves the results in a file.

    The OsmChange file is send to the server at root as the oauth user.

    :rtype : str
    :param readpath: string - file system path of OsmChange to upload
    :param writepath: string - file system path to create with response
    :param root: string - base url of OSM API 0.6 server.
    :param oauth: oauth object representing the credentials of the current user
    :return: error message or None on success
    """
    with open(readpath, 'rb') as fr:
        with open(writepath, 'wb') as fw:
            error, data = upload_bytes(fr.read(), root, oauth)
            if not error:
                fw.write(data)
            else:
                return error


def test():
    url, tokens = setup('local')
    error = upload('./test_POI.osm', './test_POI_ids.csv', url, tokens)
    if error:
        print error
    else:
        print "Upload successful."


if __name__ == '__main__':
    test()
