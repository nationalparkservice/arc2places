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
        self.name = name
        self.max_waynodes = None
        self.max_elements = None
        self.version = '0.6'
        self.server_available = False
        self.called_capabilities = False
        self._verbose = False
        self.username = os.getenv('USERNAME')
        self.oauth = None
        self.error = None
        
        # TODO: Sort this out, use name or baseurl to pick server style
        self.baseurl = baseurl

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

    def connect(self):
        self.baseurl = secrets[self.name]['url']
        client_token = secrets[self.name]['consumer_key']
        client_secret = secrets[self.name]['consumer_secret']

        # Get Request Tokens
        request_url = self.baseurl + '/oauth/request_token'
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
        auth_url = self.baseurl + '/oauth/add_active_directory_user'
        error, userid, username = self.getuseridentity(request_tokens)
        if error:
            # FIXME: clean up error message
            self.error = error + userid + username
            self.oauth = None
            return

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
            # FIXME: clean up error message
            self.error =  'Authorization Error' + str(res.status_code) + res.text
            self.oauth = None
            return

        if self._verbose:
            print "Authorized user", res.text

        # Get Access Tokens
        access_url = self.baseurl + '/oauth/access_token'
        if self._verbose:
            print "Getting Access Tokens from", access_url
        auth = ('OAuth ' +
                'oauth_token="' + request_tokens['oauth_token'] + '", ' +
                'oauth_token_secret="' + request_tokens['oauth_token_secret'] + '"')
        header = {'authorization': auth}
        res = requests.request('post', url=access_url, headers=header)
        if res.status_code != 200:
            self.error = 'Access Error' + str(res.status_code) + res.text
            self.oauth = None
            return

        access_tokens = self.simplifydict(urlparse.parse_qs(res.text))
        if self._verbose:
            print "Access Token", access_tokens['oauth_token']
            print "Access Secret", access_tokens['oauth_token_secret']

        # Initialize the Oauth object to create signed requests
        self.oauth = OAuth1Session(client_token,
                                   client_secret=client_secret,
                                   resource_owner_key=access_tokens['oauth_token'],
                                   resource_owner_secret=access_tokens['oauth_token_secret'])
        return

    def getuseridentity(self, request_tokens):
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

    def createchangeset(self, author, comment=None):
        # return Error (str), Changeset Id (str)
        if not self.oauth:
            self.connect()
        if not self.oauth:
            return None
        if not author:
            self.error = 'No Changeset author provided'
            return None
        if self._verbose:
            print 'Create change set'
        url = self.baseurl + '/api/' + self.version + '/changeset/create'
        osm_changeset_payload = ('<osm><changeset>'
                                 '<tag k="created_by" v="{0}"/>').format(author)
        if comment:
            osm_changeset_payload += '<tag k="comment" v="upload of OsmChange file"/>'
        osm_changeset_payload += '</changeset></osm>'
        try:
            resp = self.oauth.put(url,
                             data=osm_changeset_payload,
                             headers={'Content-Type': 'text/xml'})
        except requests.exceptions.ConnectionError:
            self.error =  "Unable to Connect to " + self.baseurl
            return None
        if resp.status_code != 200:
            baseerror = "Failed to open changeset. Status: {0}, Response: {0}"
            self.error = baseerror.format(resp.status_code, resp.text)
            return None
        else:
            cid = resp.text
        if self._verbose:
            print "Created change set", cid
        return cid

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
