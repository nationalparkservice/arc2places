#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
from io import open  # slow but python 3 compatible
import optparse
import sys
import os
import datetime
import tempfile
from OsmApiServer import OsmApiServer, Places
from Logger import Logger
from DataTable import DataTable


class UploadError(BaseException):
    pass


def make_upload_log(diff_result, uploaddata, date, cid, user, logger=None):
    """

    :param diff_result: byte array (string) with utf encoded xml
    :param uploaddata:  unicode data
    :param date:
    :param cid:
    :param user:
    :param logger:
    :return:
    """
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
    root = Et.fromstring(uploaddata.encode('utf-8'))
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
                if tag.attrib['k'] == 'nps:source_system_key_value':
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


def make_upload_log_from_files(upload_path, response_path, logger):
    with open(upload_path, 'r', encoding='utf-8') as fr:
        data = fr.read()
    with open(response_path, 'r', encoding='utf-8') as fr:
        resp = fr.read()
    # Assume there is only one changeset for the upload/response.
    date = None  # FIXME: get this from the changeset of the first element in the response object
    cid = None  # FIXME: get this from the changeset of the first element in the response object
    user = None  # FIXME: get this from the changeset of the first element in the response object
    return make_upload_log(data, resp, date, cid, user, logger)


def fixchangefile(cid, data):
    i = 'changeset="-1"'
    o = 'changeset="' + cid + '"'
    return data.replace(i, o)


# Public - called by PushUploadToPlaces in arc2places.pyt; test(), cmdline() in self;
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
    with open(filepath, 'r', encoding='utf-8') as fr:
        return upload_osm_data(fr.read(), server, comment, csv_path, logger)


# Public - called by SeedPlaces in arc2places.pyt; upload_osm_file() in self;
def upload_osm_data(data, server, comment=None, csv_path=None, logger=None):
    """
    Uploads contents of an OsmChange file to an OSM API server and returns the upload details as a DataTable

    Raises UploadError if there are any problems communicating with the server
    Raises IOError if there are problems writing to csv_path

    :param data: unicode containing the contents of the change file to upload
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

    if server.error:
        # Errors uploading the changeset are fatal
        # Ignore any error we got trying to close the changeset
        upload_error = server.error
        try:
            server.close_changeset(cid)
        finally:
            raise UploadError("Server did not accept the upload request.\n\tDetails: " + upload_error)
    # optional debug output
    try:
        logger.debug('\n' + resp + '\n')
    except AttributeError:
        pass

    # if there is no error then first try to create the upload_log before closing the changeset
    # Closing the changeset may fail (time-out) when it actually succeeds (eventually).
    try:
        upload_log = make_upload_log(resp, data, timestamp, cid, server.username, logger)
    except UploadError as e:
        # response isn't valid
        raise e
    except Exception as e:
        # response is valid, but there was an unexpected (programming?) error,
        f = tempfile.NamedTemporaryFile(delete=False, prefix='osmchange_')
        osm_filename = f.name
        f.close()
        f = tempfile.NamedTemporaryFile(delete=False, prefix='placesresp_')
        resp_filename = f.name
        f.close()
        try:
            logger.warn('There was a problem creating the upload log.'
                        '\nThe OSM Change file will be saved as "{0}".'
                        '\nThe server response will be saved as "{1}".'
                        '\nYou can use these to create the upload log'
                        'once the outstanding issues have been resolved.'
                        '\n\tDetails: {0}'.format(osm_filename, resp_filename, e))
        except AttributeError:
            pass
        try:
            with open(osm_filename, 'w', encoding='utf-8') as f:
                f.write(data)
        except IOError as e:
            try:
                logger.error('Error saving the OSM Change file.\n' + e.message)
            except AttributeError:
                pass
        try:
            with open(resp_filename, 'w', encoding='utf-8') as f:
                f.write(data)
        except IOError as e:
            try:
                logger.error('Error saving the server response.\n' + e.message)
            except AttributeError:
                pass
        raise e
    if csv_path and upload_log:
        upload_log.export_csv(csv_path)
        try:
            logger.info("Saved link table as CSV file.")
        except AttributeError:
            pass

    # close the changeset; Errors closing the changeset are non-fatal
    try:
        server.close_changeset(cid)
    except Exception as e:
        try:
            logger.warn('Places could not close the change request.\n\tDetails: {0}'
                        '\nThe change was uploaded, and may still be processed correctly.'
                        '\nCheck the Places editor shortly to validate your upload.'
                        '\nContact the NPMap team regarding change #{1} if there are problems.'.format(e, cid))
        except AttributeError:
            pass
    if server.error:
        try:
            logger.warn('Places could not close the change request.\n\tDetails: {0}'
                        '\nThe change was uploaded, and may still be processed correctly.'
                        '\nCheck the Places editor shortly to validate your upload.'
                        '\nContact the NPMap team regarding change #{1} if there are problems.'
                        .format(server.error, cid))
        except AttributeError:
            pass

    return upload_log


def test():
    api_server = OsmApiServer('test')
    api_server.turn_verbose_on()
    api_server.logger = Logger()
    api_server.logger.start_debug()
    upload_osm_file('./testdata/test_roads.osm', api_server, 'Testing upload OSM file function',
                    './testdata/test_roads_sync.csv', api_server.logger)
    # table = upload_osm_file('./testdata/test_poi.osm', api_server, 'Testing upload OSM file function',
    #                         None, api_server.logger)
    # table.export_arcgis('./testdata/test.gdb', 'poi_sync')


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
