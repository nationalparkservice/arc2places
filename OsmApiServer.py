"""This module provides classes that communicate with Open Street Map (OSM) API servers"""

import os
import sys
import urlparse
import json
import xml.etree.ElementTree as eTree

try:
    from requests_oauthlib import OAuth1Session
except ImportError:
    OAuth1Session = None
    print("requests_oauthlib is needed.  Add it to your system with:")
    if os.name == 'nt':
        pydir = os.path.dirname(sys.executable)
        print(pydir + r'\Scripts\pip.exe install requests_oauthlib')
        if not os.path.exists(pydir + r'\Scripts\pip.exe'):
            print('However, You must first install pip')
            print 'Download <https://bootstrap.pypa.io/get-pip.py> to ' + pydir + r'\Scripts\get-pip.py'
            print 'Then run'
            print sys.executable + ' ' + pydir + r'\Scripts\get-pip.py'
    else:
        print("sudo easy_install pip #if you do not have pip")
        print("sudo pip install requests_oauthlib")
    sys.exit()
import requests


# Before accessing resources you will need to obtain a few credentials from
# your provider (i.e. OSM) and authorization from the user for whom you wish
# to retrieve resources for.
from secrets import *


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


class OsmApiServer:

    version = '0.6'

    def __init__(self, name=''):
        self.error = None
        self.logger = None
        self.name = name
        self.username = os.getenv('USERNAME')

        self._baseurl = secrets[self.name]['url']
        self._called_capabilities = False
        self._debug = False
        self._max_waynodes = None
        self._max_elements = None
        self._oauth = None
        self._server_accepts_version = None
        self._status = None
        self._verbose = False

    def turn_verbose_on(self):
        self._verbose = True
        
    def turn_verbose_off(self):
        self._verbose = True

    def get_max_waynodes(self):
        if self._max_waynodes is None and not self._called_capabilities:
            self._get_capabilities()
        return self._max_waynodes

    def get_max_elements(self):
        if self._max_elements is None and not self._called_capabilities:
            self._get_capabilities()
        return self._max_elements

    def is_online(self):
        if self._status is None and not self._called_capabilities:
            self._get_capabilities()
        return self._status == 'online'

    def is_version_supported(self):
        if self._server_accepts_version is None and not self._called_capabilities:
            self._get_capabilities()
        return self._server_accepts_version

    def refresh_capabilities(self):
        self._get_capabilities()

    def _get_capabilities(self):
        if not self._baseurl:
            self.error = "'" + self.name + "' is not a well known server name.  Add it to secrets.py"
            return
        capabilities_url = self._baseurl + '/api/capabilities'
        if self._verbose and self.logger:
            self.logger.info("Getting capabilities from " + capabilities_url)
        resp = requests.get(capabilities_url)
        if self._debug and self.logger:
            self.logger.debug('status ' + str(resp.status_code) + '\ntext ' + resp.text)
        self._called_capabilities = True
        if resp.status_code != 200:
            baseerror = "Get cababilities failed. Status: {0}, Response: {0}"
            self.error = baseerror.format(resp.status_code, resp.text)
            return
        try:
            root = eTree.fromstring(resp.text)
        except eTree.ParseError:
            self.error = 'Get cababilities response is not valid XML.'
            return
        min_version = None
        max_version = None
        try:
            api = root[0]
            for child in api:
                if child.tag == 'version':
                    min_version = float(child.attrib['minimum'])
                    max_version = float(child.attrib['maximum'])
                if child.tag == 'waynodes':
                    self._max_waynodes = int(child.attrib['maximum'])
                if child.tag == 'changesets':
                    self._max_elements = int(child.attrib['maximum_elements'])
                if child.tag == 'status':
                    self._status = child.attrib['api']
        except (KeyError, ValueError):
            self.error = 'XML returned by get capabilities not in standard format'
            return
        self._server_accepts_version = min_version <= float(self.version) <= max_version
        if self._verbose and self.logger:
            self.logger.info("Got capabilities")

    def _connect(self):
        if not OAuth1Session:
            self.error = "requests_oauthlib module not loaded."
            return
        if not self._baseurl:
            self.error = "'" + self.name + "' is not a well known server name.  Add it to secrets.py"
            return

        client_token = secrets[self.name]['consumer_key']
        client_secret = secrets[self.name]['consumer_secret']

        # Get Request Tokens
        request_url = self._baseurl + '/oauth/request_token'
        if self._verbose and self.logger:
            self.logger.info("Getting Request Tokens from " + request_url)
        if self._debug and self.logger:
            self.logger.debug("Client Token: " + client_token)
            self.logger.debug("Client Secret: " + client_secret)
        resp = requests.post(request_url, None)
        if resp.status_code != 200:
            baseerror = "Request Error. Status: {0}, Response: {0}"
            self.error = baseerror.format(resp.status_code, resp.text)
            self._oauth = None

        request_tokens = simplifydict(urlparse.parse_qs(resp.text))
        if self._debug and self.logger:
            self.logger.debug("Request Token: " + request_tokens['oauth_token'])
            self.logger.debug("Request Secret: " + request_tokens['oauth_token_secret'])

        # Authorize User
        if self.name == 'places' or self.name == 'test':
            if not self._authorize_npsuser(request_tokens):
                return
        else:
            self.error = 'OSM user authentication not yet supported'
            return

        # Get Access Tokens
        access_url = self._baseurl + '/oauth/access_token'
        if self._verbose and self.logger:
            self.logger.info("Getting Access Tokens from " + access_url)
        auth = ('OAuth ' +
                'oauth_token="' + request_tokens['oauth_token'] + '", ' +
                'oauth_token_secret="' + request_tokens['oauth_token_secret'] + '"')
        header = {'authorization': auth}
        res = requests.request('post', url=access_url, headers=header)
        if res.status_code != 200:
            self.error = 'Access Error' + str(res.status_code) + res.text
            self._oauth = None
            return

        access_tokens = simplifydict(urlparse.parse_qs(res.text))
        if self._debug and self.logger:
            self.logger.debug("Access Token: " + access_tokens['oauth_token'])
            self.logger.debug("Access Secret: " + access_tokens['oauth_token_secret'])

        # Initialize the Oauth object to create signed requests
        self._oauth = OAuth1Session(client_token,
                                    client_secret=client_secret,
                                    resource_owner_key=access_tokens['oauth_token'],
                                    resource_owner_secret=access_tokens['oauth_token_secret'])
        return

    def _authorize_npsuser(self, request_tokens):
        if self._verbose and self.logger:
            self.logger.info("Authorizing NPS user")
        auth_url = self._baseurl + '/oauth/add_active_directory_user'
        error, userid, username = self._get_npsuser_identity()
        if error:
            baseerror = error + ". Userid: {0}, Username: {0}"
            self.error = baseerror.format(userid, username)
            self._oauth = None
            return False

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
            baseerror = "Authorization Error. Status: {0}, Response: {0}"
            self.error = baseerror.format(res.status_code, res.text)
            self._oauth = None
            return False
        if self._verbose and self.logger:
            self.logger.info("Authorized NPS user " + username)
        return True

    def _get_npsuser_identity(self):
        if not self.username:
            return 'User Error', 0, 'No user given'

        if self._verbose and self.logger:
            self.logger.info("Looking up id for user " + self.username)

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
        if userid is None:
            msg = ("There is no Places account for 'nps\{0}'.\n"
                   "Sign in at {0} to create your account.").format(
                self.username, "https://insidemaps.nps.gov/account/logon/")
            return msg, None, None
        if self._verbose and self.logger:
            self.logger.info("Found id " + userid)
        return None, userid, displayname

    def create_changeset(self, application, comment=None):
        """
        Uses the credentials of the current user to open a change set.

        :rtype : int
        :param application: The name of the application creating the changeset
        :param comment: A optional comment to describe the changeset
        :return: returns None on error, or the changeset id as a positive int
        """

        if not self._oauth:
            self._connect()
        if not self._oauth:
            # self.error should be set by self._connect()
            if not self.error:
                self.error = 'Unexpected failure authenticating {0} on {1}'.format(self.username, self.name)
            return None
        if not application:
            self.error = 'No application name provided for the changeset'
            return None
        if self._verbose and self.logger:
            self.logger.info('Create change set')
        url = self._baseurl + '/api/' + self.version + '/changeset/create'
        osm_changeset_payload = ('<osm><changeset>'
                                 '<tag k="created_by" v="{0}"/>').format(application)
        if comment:
            osm_changeset_payload += '<tag k="comment" v="upload of OsmChange file"/>'
        osm_changeset_payload += '</changeset></osm>'
        try:
            resp = self._oauth.put(url, data=osm_changeset_payload,
                                   headers={'Content-Type': 'text/xml'})
        except requests.exceptions.ConnectionError:
            self.error = "Unable to Connect to " + self._baseurl
            return None
        except Exception as e:
            baseerror = "Unexpected exception:\n{0}\nPUTing:\n{1}\nto {2}"
            self.error = baseerror.format(e, osm_changeset_payload, url)
            return None
        if resp.status_code == 400:
            self.error = 'There are errors parsing the XML'
            return None
        if resp.status_code != 200:
            baseerror = "Failed to open changeset. Status: {0}, Response: {0}"
            self.error = baseerror.format(resp.status_code, resp.text)
            return None
        else:
            cid = resp.text
        if self._verbose and self.logger:
            self.logger.info("Created change set " + cid)
        return cid

    def upload_changeset(self, cid, change):
        """
        Uploads an osm changefile to an open changest (cid)

        :param cid: string - the id of the open changeset
        :param change: unicode - the content of an osm change file
        :return: returns the api upload response xml or None on error
        """

        if not self._oauth:
            self._connect()
        if not self._oauth:
            return None
        url = self._baseurl + '/api/' + self.version + '/changeset/' + cid + '/upload'
        if self._verbose and self.logger:
            self.logger.info('Upload to change set ' + cid)
        try:
            resp = self._oauth.post(url, data=change.encode('utf-8'), headers={'Content-Type': 'text/xml'})
        except requests.ConnectionError as e:
            baseerror = "Failed to upload changeset. ConnectionError: {0}"
            self.error = baseerror.format(e)
            return None
        except Exception as e:
            baseerror = u"Unexpected exception:\n{0}\nPOSTing:\n{1}\nto {2}"
            self.error = baseerror.format(e, change, url)
            return None
        if resp.status_code != 200:
            baseerror = "Failed to upload changeset. Status: {0}, Response: {0}"
            self.error = baseerror.format(resp.status_code, resp.text)
            data = None
        else:
            self.error = None
            data = resp.text
            if self._verbose and self.logger:
                self.logger.info("Uploaded change set successfully")
        return data

    def close_changeset(self, cid):
        """
        Closes the changeset provided.

        :param cid: String, The id (number) of a changeset opened by the current user
        :return: No return value, check error property for errors
        """
        if not self._oauth:
            self._connect()
        if not self._oauth:
            return
        if not cid:
            self.error = 'No changeset id provided'
            return
        if self._verbose and self.logger:
            self.logger.info("Close change set " + cid)
        url = self._baseurl + '/api/' + self.version + '/changeset/' + cid + '/close'
        try:
            resp = self._oauth.put(url)
        except requests.Timeout:
            self.error = 'Timeout error closing changeset'
            return
        except Exception as e:
            self.error = 'Unexpected exception:\n{0}\nPUTing: {1}'.format(e, url)
            return
        if resp.status_code == 404:
            self.error = 'No changeset with the given id could be found'
            return
        if resp.status_code == 409:
            if resp.text:
                self.error = resp.text
            else:
                self.error = 'The user trying to update the changeset is not the same as the one that created it'
            return
        if resp.status_code != 200:
            self.error = 'Unknown failure (' + str(resp.status_code) + ') closing changeset'
            return
        self.error = None
        if self._verbose and self.logger:
            self.logger.info("Closed change set successfully")


class Places(OsmApiServer):
    def __init__(self):
        OsmApiServer.__init__(self, name='places')


class Osm(OsmApiServer):
    def __init__(self):
        OsmApiServer.__init__(self, name='osm')


if __name__ == '__main__':
    import Logger
    places = Places()
    places.turn_verbose_on()
    places.logger = Logger.Logger()
    places._debug = True
    online = places.is_online()
    if places.error is not None:
        print 'ERROR', places.error
    else:
        print 'is online', online
        print 'is version supported', places.is_version_supported()
        print 'max_waynodes', places.get_max_waynodes()
        print 'max_elements', places.get_max_elements()
