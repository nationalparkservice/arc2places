#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import os
import utils
import sys
import urllib2
import arcpy

# Before accessing resources you will need to obtain a few credentials from
# your provider (i.e. OSM) and authorization from the user for whom you wish
# to retrieve resources for.
from secrets import *


def find_synctable(fc):
    return None, ""


def build_changes(fc, outfile, options):
    if options.verbose:
        utils.info(u"Preparing to convert '{0:s}' to '{1:s}'."
                   .format(fc, outfile))

    if not options.synctable:
        options.synctable = find_synctable(fc)
    if not options.synctable:
        return (u"Sync table not specified and default table does not exist.",
                None)
    if not arcpy.Exists(options.synctable):
        return u"Sync table {0:s} not found.".format(options.synctable), None
    if not arcpy.Describe(fc).editorTrackingEnabled:
        return u"Editor tracking must be enabled on the feature class.", None
    editdate_fieldname = arcpy.Describe(fc).editedAtFieldName
    
    """
    get lastupdate with select top 1 from synctable order by editdate_fieldname DESC
    find the new features:
      select * from dataset join with synctable on DS.geometyryid = synctable.geometryid is null where synctable.geometryid is null
      run these features through the translator to ceated the insert records same as the initial seeding operation
      
    find the deleted features
      select placesid from synctable join dataset on geometryid where dataset.geometryid is null
      for each feature, get the data from places:  http://10.147.153.193/api/0.6/node/xxx (or way)
      extract the data needed to create an osm change delete record
      
    for the updates:
      select *, s.placeid from dataset join synctable as s where editdate_fieldname > lastupdate
      for each feature get the existing data from places (http://10.147.153.193/api/0.6/node/xxx)
      and merge it with the feature run through the translator to create an osm change update record (looks the same as an insert record)
      with a new version number
    """

        # options.translations = loadtranslations(options)

    
    error, data = None, ""  # output_xml(options) # FIXME
    if outfile:
        with open(outfile, 'wb') as fw:
            fw.write(data)
        if options.verbose:
            utils.info(u"Wrote {0:d} elements to file '{1:s}'"
                       .format(1, outfile))  # FIXME
    else:
        if options.verbose:
            utils.info(u"Returning {0:d} converted elements"
                       .format(1))  # FIXME
        return error, data


class DefaultOptions:
    debug = False
    verbose = False
    translator = 'generic'
    synctable = None


def test():
    opts = DefaultOptions()
    opts.verbose = True

    featureclass = './tests/test_parking_pids.csv'
    osmchangefile = './tests/test_Parking.osm'

    error = build_changes(featureclass, osmchangefile, opts)
    if error:
        print error
    else:
        print "Done."


def cmdline():
    # Setup program usage
    usage = """%prog [Options] SRC DST
    or:    %prog --help

    Creates a file called DST from changes in SRC.
    SRC is an ArcGIS feature class
    DST is a OSM change file
    to the id numbers assigned in Places."""

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-t", "--translator", dest="translator", type=str, help=(
        "Name of translator to convert ArcGIS features to OSM Tags. " +
        "Defaults to Generic."), default='Generic')
    parser.add_option("-s", "--synctable", dest="synctable", type=str, help=(
        "Name of table with the IDs and dates of features written to Places "
        "for this feature class." +
        "Defaults to table called {SRC}_places_sync."), default=None)
    parser.set_defaults(verbose=False)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="Write processing step details to stdout.")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="Write debugging details to stdout.")
    parser.set_defaults(verbose=False)

    # Parse and process arguments
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error(u"You must specify a source and destination")
    elif len(args) > 2:
        parser.error(u"You have specified too many arguments.")

    # Input and output file
    featureclass = args[0]
    osmchangefile = args[1]
    if not os.path.exists(featureclass):
        parser.error(u"The input file does not exist.")
    if os.path.exists(osmchangefile):
        parser.error(u"The destination file exist.")
    error = build_changes(featureclass, osmchangefile, options)
    if error:
        print error
    else:
        print "Done."


if __name__ == '__main__':
    test()
    #cmdline()
