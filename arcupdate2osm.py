#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import os
import sys
# import urllib2
import arcpy
from OsmApiServer import OsmApiServer
from Translator import Translator
from Logger import Logger


def arc_build_osm_change_xml(features, synctable, translator, server, options=None):
    # returns error, xml
    if not isinstance(features, basestring):
        raise TypeError('features is the wrong type; a basestring is expected')
    if not isinstance(synctable, basestring):
        raise TypeError('synctable is the wrong type; a basestring is expected')
    if not isinstance(translator, Translator):
        raise TypeError('translator is the wrong type; a Translator is expected')
    if not isinstance(server, OsmApiServer):
        raise TypeError('server is the wrong type; an OsmApiServer is expected')
    if not arcpy.Exists(features):
        raise ValueError("features '{0:s}' does not exist".format(features))
    if not arcpy.Exists(synctable):
        raise ValueError("synctable '{0:s}' does not exist".format(synctable))
    if options and options.verbose and options.logger:
        options.logger.info(u"Searching '{0:s}' for changes from '{0:s}'.".format(features, synctable))
    if not arcpy.Describe(features).editorTrackingEnabled:
        return u"Editor tracking must be enabled on the feature class.", None

    """
    Example input data
    feature table: (id, status, edit date)
        A, public, t0
        B, not public, t0
        C, public, t0
        D, public, t0
        E, not public, t0
        F, public, t0
        G, not public, t0
    sync table: (action, gis id, place id, upload timestamp)
        create, A, 1, t1
        create, C, 2, t1
        create, D, 3, t1
        create, F, 4, t1
    updated feature table: (id, status, editdate)
        A, not public, t2
        B, public, t2
        C, public, t2
        D, -- deleted --
        E, not public, t2
        F, public, t0
        G, not public, t0
        H, public, t2
        I, not public, t2
    Change set for places:
        Create: [B, H]
        Delete: [1, 3]
        Update: [(C,2)]
    Update sync table
        create, A, 1, t1
        create, C, 2, t1
        create, D, 3, t1
        create, F, 4, t1
        create, B, 5, t3
        create, H, 6, t3
        delete, A, 1, t3
        delete, D, 1, t3
        update, C, 2, t3
    """

    """
    editdate_fieldname = arcpy.Describe(fc).editedAtFieldName
    lastupdate = select top 1 from synctable order by editdate_fieldname DESC

    # new features
    featureset = select * from dataset left join synctable
                 on dataset.geometyryid = synctable.geometryid
                 where synctable.geometryid is null
                 # returns (B,E,G,H,I) from above example
                 # arc2osm will filter out features that should not be added because they are not public
                 # returns (B,H)
    # TODO: fix arc2osmcode to return xml tree and take a searchcursor (or list of ids)
    xml = arc2osmcore.process(feature_set, translator, options)

    # find the deleted features
    delete_xml = Et.Element('delete')
    [features_for_places] = translator.filter_data_set(dataset)  # removes features that were public and are now not
                                                                 # returns (B,C,F,H)
    [(element_type, places_id)] = select placesid from synctable left join [features_for_places]
                                  on geometryid where dataset.geometryid is null
                                  # returns (1,3)
    if [(element_type, places_id)]:
        delete_xml = create delete node
        for element_type, places_id in [(element_type, places_id)]:
           element_xml = places.get_element_xml('http://10.147.153.193/api/0.6/{{element_type}}/{{places_id}}/full')
                # removes ways from relation if they are in other relations
                #   if get /api/0.6/way/#id/relations > 1
                # removes nodes if they are in other ways or relations (maybe only check first/last nodes):
                #   if get http://10.147.153.193/api/0.6/node/{node}/ways > 1
                #
                # alternative (less load on server) support DELETE /api/0.6/[node|way|relation]/#id
                #   nice to remove version from payload, and skip sub-elements which are in use or interesting
    delete_xml.append(element_xml)
    xml.append(delete_xml)

    # updates:
      select *, s.placeid from dataset join synctable as s where editdate_fieldname > lastupdate
      # returns [(A,1), (C,2)]
      # use arc2osm to create a set of OSM creates (same format is used for the update)
      # arc2osm will filter out features that should not be added because they are not public
      # returns [(C,2)]
      # for each feature get the existing data from places (http://10.147.153.193/api/0.6/{{element_type}}/{{places_id}}/full)
      # (optional) need to add any attributes in places that are not in eGIS (or they will get removed)
      # compare ways/nodes in relationships one by one, and move to 'delete' any elements in places but not in GIS, need to check if used in other relationships
      # compare vertices in ways one by one, and move to 'delete' any elements in places but not in GIS, need to check if used in other ways/relationships
      #                                              and (optionally) remove any from update if there is no change
      #      maybe do not remove the sub element from the way/relationship, but keep in places - it should probably be removed if it is unused and uninteresting (maybe happens in a places cleanup)
      # update the version number place holder from arc2osm with the correct version number from places
    """


class DefaultOptions:
    debug = False
    verbose = False
    logger = None


def test():
    logger = Logger()
    opts = DefaultOptions()
    opts.verbose = True
    opts.debug = True
    opts.logger = logger

    featureclass = './tests/test.gdb/PARKINGLOTS_py'
    logtable = './tests/test_parking_log.csv'
    osmchangefile = './tests/test_Parking_update.osm'
    translator = Translator.get_translator('parkinglots')
    api_server = OsmApiServer('test')
    api_server.logger = logger
    api_server.turn_verbose_on()
    error, xml = arc_build_osm_change_xml(featureclass, logtable, translator, api_server, opts)
    if error:
        print error
    else:
        data = Et.tostring(xml, encoding='utf-8')
        with open(osmchangefile, 'wb') as fw:
            fw.write(data)
        print "Done."


def cmdline():
    # Setup program usage
    usage = """%prog [Options] SRC LOG DST
    or:    %prog --help

    Creates a file called DST from changes in SRC compared to LOG.
    SRC is an ArcGIS feature class
    LOG is an ArcGIS table that describes the features sent to places
    DST is a OSM change file
    """

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-t", "--translator", dest="translator", type=str, help=(
        "Name of translator to convert ArcGIS features to OSM Tags. " +
        "Defaults to Generic."), default='generic')
    parser.add_option("-s", "--server", dest="server", type=str, help=(
        "Name of server to connect to. I.e. 'places', 'osm', 'osm-dev', 'local'." +
        "Defaults to 'places'.  Name must be defined in the secrets file."), default='places')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="Write processing step details to stdout.")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="Write debugging details to stdout.")
    parser.add_option("--changeset-id", dest="changesetId", type=int,
                      help="Sentinal ID number for the changeset.  Only used " +
                           "when an osmChange file is being created. " +
                           "Defaults to -1.", default=-1)

    parser.set_defaults(verbose=False, debug=False)

    # Parse and process arguments
    (options, args) = parser.parse_args()

    if len(args) < 3:
        parser.error(u"You must specify a source, log and destination")
    elif len(args) > 3:
        parser.error(u"You have specified too many arguments.")

    # Input and output file
    featureclass = args[0]
    logtable = args[1]
    osmchangefile = args[2]
    if os.path.exists(osmchangefile):
        parser.error(u"The destination file exist.")
    # Translator
    translator = Translator.get_translator(options.translator)
    # API Server
    if options.server:
        api_server = OsmApiServer(options.server)
    else:
        api_server = OsmApiServer('places')
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
    # Build Change XML
    # TODO: do exception checking
    error, xml = arc_build_osm_change_xml(featureclass, logtable, translator, api_server, options)
    # Output results
    if error:
        print error
    else:
        # TODO: do exception checking
        data = Et.tostring(xml, encoding='utf-8')
        with open(osmchangefile, 'wb') as fw:
            fw.write(data)
        print "Done."


if __name__ == '__main__':
    test()
    # cmdline()
