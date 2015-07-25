__author__ = 'RESarwas'

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


class OsmApiServer:
    def __init__(self, name='', baseurl=''):
        self.max_waynodes = None
        self.max_elements = None
        self.server_available = False
        self.called_capabilities = False
        self._verbose = False
        self.username = os.getenv('USERNAME')
        
        # TODO: Sort this out, use name or baseurl to pick server style
        self.baseurl = baseurl
        self.error, self.baseurl, self.tokens = self.setup(name)

    def turn_verbose_on(self):
        self._verbose = True
        
    def turn_verbose_off(self):
        self._verbose = True
        
    def get_capabilities(self):
        def get_capabilities_from_server():
            self.called_capabilities = True
            # TODO: implement call baseurl/api/capabilities and parse results

            return 50000, 500000

        if not self.max_waynodes:
            self.max_waynodes, self.max_elements = get_capabilities_from_server()

        return self.max_waynodes, self.max_elements

    # TODO Add other properties
    # TODO Add functions from osm2places

    def setup(self, site, options=None):
        url = secrets[site]['url']
        client_token = secrets[site]['consumer_key']
        client_secret = secrets[site]['consumer_secret']

        # Get Request Tokens
        request_url = url + '/oauth/request_token'
        if self._verbose:
            print "Getting Request Tokens from", request_url
            print "Client Token", client_token
            print "Client Secret", client_secret
        res = requests.post(request_url, None)
        if res.status_code != 200:
            return 'Request Error', res.status_code, res.text

        request_tokens = self.simplifydict(urlparse.parse_qs(res.text))
        if self._verbose:
            print "Request Token", request_tokens['oauth_token']
            print "Request Secret", request_tokens['oauth_token_secret']

        # Authorize User
        if self._verbose:
            print "Authorizing user"
        auth_url = url + '/oauth/add_active_directory_user'
        error, userid, username = self.getuseridentity(site, request_tokens, options)
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
        if self._verbose:
            print "Authorized user", res.text

        # Get Access Tokens
        access_url = url + '/oauth/access_token'
        if self._verbose:
            print "Getting Access Tokens from", access_url
        auth = ('OAuth ' +
                'oauth_token="' + request_tokens['oauth_token'] + '", ' +
                'oauth_token_secret="' + request_tokens['oauth_token_secret'] + '"')
        header = {'authorization': auth}
        res = requests.request('post', url=access_url, headers=header)
        if res.status_code != 200:
            return 'Access Error', res.status_code, res.text

        access_tokens = self.simplifydict(urlparse.parse_qs(res.text))
        if self._verbose:
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
    def getuseridentity(self, site, request_tokens, options=None):
        if not self.username:
            return 'User Error', 0, 'No user given'

        if self._verbose:
            print "Looking up id for user", self.username

        req = 'http://insidemaps.nps.gov/user/lookup?query=' + self.username
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
        if self._verbose:
            print "Found id", userid
        return None, userid, displayname

    def simplifydict(self, dictoflists):
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

    def openchangeset(self, oauth, root):
        # return Error (str), Changeset Id (str)
        if self._verbose:
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
        if self._verbose:
            print "Created change set", cid
        return None, cid

    def uploadchangeset(self, oauth, root, cid, change, options=None):
        # return Error (str), Upload Response (str)
        path = root + '/api/0.6/changeset/' + cid + '/upload'
        if self._verbose:
            print 'Upload to change set', cid
        resp = oauth.post(path, data=change, headers={'Content-Type': 'text/xml'})
        if resp.status_code != 200:
            baseerror = "Failed to upload changeset. Status: {0}, Response: {0}"
            error = baseerror.format(resp.status_code, resp.text)
            return error, None
        else:
            data = resp.text
            if self._verbose:
                print "Uploaded change set successfully"
                # print "response",data
        return None, data

    def closechangeset(self, oauth, root, cid, options=None):
        if self._verbose:
            print "Close change set", cid
        oauth.put(root + '/api/0.6/changeset/' + cid + '/close')
        if self._verbose:
            print "Closed change set successfully"

    def fixchangefile(self, cid, data):
        i = 'changeset="-1"'
        o = 'changeset="' + cid + '"'
        return data.replace(i, o)


class Places(OsmApiServer):
    def __init__(self):
        OsmApiServer.__init__(self, name='places')

class Osm(OsmApiServer):
    def __init__(self):
        OsmApiServer.__init__(self, name='osm')
