#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import sys
import os
import datetime
from OsmApiServer import OsmApiServer, Places
from Logger import Logger
from DataTable import DataTable


class UploadError(BaseException):
    pass


def make_upload_log(diff_result, uploaddata, date, cid, user, logger=None):
    try:
        logger.info("Create link table from upload data and response")
    except AttributeError:
        pass
    placesids = {}
    try:
        root = Et.fromstring(diff_result)
    except Et.ParseError:
        raise UploadError("Response from server is not valid XML.\nResponse:\n" + diff_result)
    if root.tag != "diffResult":
        raise UploadError("Response from server is not a diffResult\nResponse:\n" + diff_result)
    for child in root:
        version = None
        if 'new_version' in child.attrib:
            version = child.attrib['new_version']
        placesids[child.attrib['old_id']] = (child.attrib['new_id'], child.tag, version)
    gisids = {}
    root = Et.fromstring(uploaddata)
    # this must be a valid osmChange file,
    # or we wouldn't get this far, so proceed without error checking
    for child in root:
        action = child.tag  # create, delete, update
        for grandchild in child:
            source_id = None
            # skip elements with no tags (typically vertices)
            has_tags = False
            for tag in grandchild.findall('tag'):
                has_tags = True
                if tag.attrib['k'] == 'nps:source_id':
                    source_id = tag.attrib['v']
                    break
            if has_tags:
                tempid = grandchild.attrib['id']
                gisids[tempid] = (action, source_id)
    data = DataTable()
    data.fieldnames = ['date', 'user', 'changeset', 'action', 'element', 'places_id', 'version_id', 'source_id']
    data.fieldtypes = ['DATE', 'TEXT', 'LONG', 'TEXT', 'TEXT', 'TEXT', 'LONG', 'TEXT']
    for tempid in gisids:
        load = gisids[tempid]
        diff = placesids[tempid]
        row = [date, user, cid, load[0], diff[1], diff[0], diff[2], load[1]]
        data.rows.append(row)
    try:
        logger.info("Created link table.")
    except AttributeError:
        pass
    return data


def fixchangefile(cid, data):
    i = 'changeset="-1"'
    o = 'changeset="' + cid + '"'
    return data.replace(i, o)


# Public - called by PushUploadToPlaces in Places.pyt; test(), cmdline() in self;
def upload_osm_file(filepath, server, comment=None, csv_path=None, logger=None):
    """
    Uploads an OsmChange file to an OSM API server and returns the upload details as a DataTable

    Raises IOError if filepath cannot be opened/read
    Raises UploadError if there are any problems communicating with the server
    Raises IOError if there are problems writing to csv_path

    :param filepath: A filesystem path to an OsmChange file
    :param server: An OsmApiServer object (needed for places connection info)
    :param comment: A string describing the contents of the changeset
    :param csv_path: A filesystem path to save the DataTable response as a CSV file
    :param logger: A Logger object for info/warning/debug/error output
    :return: a DataTable object that can be saved as a CSV file or an ArcGIS table dataset
    :rtype : DataTable
    """
    with open(filepath, 'rb') as fr:
        return upload_osm_data(fr.read(), server, comment, csv_path, logger)


# Public - called by SeedPlaces in Places.pyt; upload_osm_file() in self;
def upload_osm_data(data, server, comment=None, csv_path=None, logger=None):
    """
    Uploads contents of an OsmChange file to an OSM API server and returns the upload details as a DataTable

    Raises UploadError if there are any problems communicating with the server
    Raises IOError if there are problems writing to csv_path

    :param data: basestring (or open(name, 'rb').read()) containing the contents of the change file to upload
    :param server: An OsmApiServer object (needed for connection info)
    :param comment: A string describing the contents of the changeset
    :param csv_path: A filesystem path to save the DataTable response as a CSV file
    :param logger: A Logger object for info/warning/debug/error output
    :return: a DataTable object that can be saved as a CSV file or an ArcGIS table dataset
    :rtype : DataTable
    """
    cid = server.create_changeset('arc2places', comment)
    if not cid:
        raise UploadError("Unable to open a changeset. Check the network, "
                          "and your permissions.\n\tDetails: " + server.error)
    timestamp = datetime.datetime.now()
    resp = server.upload_changeset(cid, fixchangefile(cid, data))
    upload_error = server.error
    server.close_changeset(cid)
    if upload_error:
        # Errors uploading the changeset are fatal
        # Ignore any error we got trying to close the changeset
        raise UploadError("Server did not accept the upload request.\n\tDetails: " + upload_error)
    if server.error:
        # Errors closing the changeset are non-fatal
        try:
            logger.warn('Server could not close the change request.\n\tDetails: ' + server.error)
        except AttributeError:
            pass
    try:
        logger.debug('\n' + resp + '\n')
    except AttributeError:
        pass
    upload_log = make_upload_log(resp, data, timestamp, cid, server.username, logger)
    if csv_path:
        upload_log.export_csv(csv_path)

    return upload_log


def test():
    api_server = OsmApiServer('test')
    api_server.turn_verbose_on()
    api_server.logger = Logger()
    api_server.logger.start_debug()
    upload_osm_file('./tests/test_roads.osm', api_server, 'Testing upload OSM file function'
                    './tests/test_roads_sync.csv', api_server.logger)


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
    parser.add_option("-s", "--server", dest="server", type=str, help=(
        "Name of server to connect to. I.e. 'places', 'osm', 'osm-dev', 'local'." +
        "Defaults to 'places'.  Name must be defined in the secrets file."), default='places')
    parser.add_option("-c", "--comment", dest="comment", type=str, help=(
                      "A description of the contents of the changeset."), default=None)
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
    if options.server:
        api_server = OsmApiServer(options.server)
    else:
        api_server = Places()
    online = api_server.is_online()
    if api_server.error:
        print api_server.error
        sys.exit(1)
    if not online:
        print "Server is not online right now, try again later."
        sys.exit(1)
    if not api_server.is_version_supported():
        print "Server does not support version " + api_server.version + " of the OSM"
        sys.exit(1)
    if options.verbose:
        api_server.logger = Logger()
        api_server.turn_verbose_on()
    if options.username:
        api_server.username = options.username
    upload_osm_file(srcfile, api_server, options.comment, dstfile, api_server.logger)


if __name__ == '__main__':
    test()
    # cmdline()
