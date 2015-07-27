#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import os
from OsmApiServer import Places


# TODO: create/return an Upload_log object that can be saved as a CSV file or an ArcGIS table dataset
# TODO: Add date, version, changeset id, and any other available info that might be helpful in sync process
def makeidmap(idxml, uploaddata, options=None):
    if options and options.verbose and options.logger:
        options.logger.info("Process response")
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
    if options and options.verbose and options.logger:
        options.logger.info("Processed response")
    return None, resp


def fixchangefile(cid, data):
    i = 'changeset="-1"'
    o = 'changeset="' + cid + '"'
    return data.replace(i, o)


# TODO: decide on error handeling protocol (exceptions, Eithers, or (Error,Data))
def upload_osm_file(filepath, server, csv_path=None, options=None):
    """
    Uploads an OsmChange file to an OSM API server and returns an upload log

    :param filepath: A filesystem path to an OSM Change file
    :param server: An Osm_api_server object (needed for places connection info)
    :param csv_path: A filesystem path to save the Upload_Log response as a CSV file
    :param options: A set of attributes that provide additional control for this method
    :return: Either an error or an Upload_log object that can be saved as a CSV file or an ArcGIS table dataset
    """
    with open(filepath, 'rb') as fr:
        return upload_osm_data(fr.read(), server, csv_path, options)


def upload_osm_data(data, server, csv_path=None, options=None):
    """
    Uploads contents of an OsmChange file to an OSM API server and returns an upload log

    :param data: unicode (or bytes as from open(name, 'rb').read()) containing the change file contents to upload
    :param server: An Osm_api_server object (needed for connection info)
    :param csv_path: A filesystem path to save the Upload_Log response as a CSV file
    :param options: A set of attributes that provide additional control for this method
    :return: Either an error or an Upload_log object that can be saved as a CSV file or an ArcGIS table dataset
    """
    cid = server.createchangeset()
    if cid:
        resp = server.uploadchangeset(cid, fixchangefile(cid, data))
        if resp:
            error, upload_log = makeidmap(resp, data, options)
            if upload_log:
                if csv_path:
                    # FIXME: upload_log does not implement this method (it is just text right now)
                    error = upload_log.save_to_csv(csv_path)
                    if error:
                        return "Failed to sve CSV. " + error, None
                else:
                    return None, upload_log
            return "Failed to relate Places and GIS date. " + error, None
        upload_error = server.error
        server.closechangeset(cid)
        close_error = server.error
        error = "Server did not accept the upload request. " + upload_error
        if close_error:
            error += '\nserver cold not close change request. ' + close_error
        return error, None
    return "Unable to open a changeset, check the network, and your permissions. " + server.error, None


def test():
    places = Places()
    places.turn_verbose_on()
    error = upload_osm_file('./tests/test_trail_routes.osm', places, './tests/test_trail_routes_pids.csv')
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
    places = Places()
    if options.verbose:
        places.turn_verbose_on()
    if options.username:
        places.username = options.username
    error = upload_osm_file(srcfile, places, dstfile, options)
    if error:
        print error
    else:
        print "Done."


if __name__ == '__main__':
    # test()
    cmdline()
