#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import os
from OsmApiServer import Places

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


# TODO: remove this method
def xxx_upload_bytes(data, options=None, server=None, user=None):
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
    error, cid = openchangeset(user, server)
    if cid:
        error, resp = uploadchangeset(user, server, cid,
                                      fixchangefile(cid, data), options)
        closechangeset(user, server, cid, options)
        if resp:
            error, idmap = makeidmap(resp, data, options)
            if idmap:
                return None, idmap
            return "Failed to relate Places and GIS date. " + error, None
        return "Server did not accept the upload request. " + error, None
    return "Unable to open a changeset, check the permissions. " + error, None


# TODO: remove this method
def xxx_upload(readpath, writepath, options=None, root=None, oauth=None):
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
        error, data = xxx_upload_bytes(fr.read(), options, root, oauth)
        if error:
            return error
        with open(writepath, 'wb') as fw:
            fw.write(data)


# TODO: decide on error handeling protocol (exceptions, Eithers, or (Error,Data))
def upload_osm_file(filepath, server, csv_path=None, options=None):
    """
    Uploads an OsmChange file to an OSM API server and returns an upload log

    :param filepath: A filesystem path to an OSM Change file
    :param server: An Osm_api_server object (needed for places connection info)
    :param csv_path: A filesystem path to save the Upload_Log response as a CSV file
    :return: Either an error or an Upload_log object that can be saved as a CSV file or an ArcGIS table dataset
    """
    # TODO: implement this method
    if csv_path and filepath and server and options:
        return filepath


def upload_osm_data(data, server, csv_path=None, options=None):
    """
    Uploads an OsmChange file to an OSM API server and returns an upload log

    :param data: bytes as from open(name, 'rb').read() containing the upload
    :param server: An Osm_api_server object (needed for places connection info)
    :param csv_path: A filesystem path to save the Upload_Log response as a CSV file
    :return: Either an error or an Upload_log object that can be saved as a CSV file or an ArcGIS table dataset
    """
    # TODO: implement this method
    if csv_path and data and server and options:
        return data


# noinspection PyClassHasNoInit
class DefaultOptions:
    username = None
    verbose = False


def test():
    opts = DefaultOptions()
    opts.verbose = True
    # TODO: import Osm_api_server
    places = None  # Osm_api_server()
    if error:
        print str(error) + ' ' + str(url) + ' ' + str(tokens)
        return

    error = upload_osm_file('./tests/test_trail_routes.osm', places, './tests/test_trail_routes_pids.csv', opts)
    if error:
        print error
    else:
        print "Done."


def cmdline():
    # Setup program usage
    usage = """%prog [Options] SRC DST
    or:    %prog --help

    Uploads SRC to Places and saves the response in DST
    SRC is an OsmChange file
    DST is a CSV file that relates the GIS ids in the change file
    to the id numbers assigned in Places."""

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-u", "--username", dest="username", type=str, help=(
        "Domain user logon name. " +
        "Defaults to None. When None, will load from " +
        "'USERNAME' environment variable."), default=None)
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
    # TODO: import and configure an Osm_api_server
    places = Places()
    error = upload_osm_file(srcfile, places, dstfile, options)
    if error:
        print error
    else:
        print "Done."


if __name__ == '__main__':
    # test()
    cmdline()
