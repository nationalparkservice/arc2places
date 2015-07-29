#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" arc2osm beta

This command line tool takes an esri featureclass and outputs an OSM file
with that data.

By default tags will be naively copied from the input data. Hooks are provided
so that, with a little python programming, you can translate the tags however
you like. More hooks are provided so you can filter or even modify the features
themselves.

To use the hooks, create a file in the translations/ directory called myfile.py
and run agr2osm.py <featureclass> -o outfile.osm -t myfile. This file should
define a function with the name of each hook you want to use. Hooks are
'filterTags', 'filterFeature', 'filterFeaturePost', and 'preOutputTransform'.

Heavily based on ogr2osm (https://github.com/pnorman/ogr2osm) released under
the following terms:

Copyright (c) 2012-2013 Paul Norman <penorman@mac.com>, Sebastiaan Couwenberg
<sebastic@xs4all.nl>, The University of Vermont <andrew.guertin@uvm.edu>

Released under the MIT license: http://opensource.org/licenses/mit-license.php

Based very heavily on code released under the following terms:

(c) Iván Sánchez Ortega, 2009
<ivan@sanchezortega.es>
###############################################################################
#  "THE BEER-WARE LICENSE":                                                   #
#  <ivan@sanchezortega.es> wrote this file. As long as you retain this notice #
#  you can do whatever you want with this stuff. If we meet some day, and you #
#  think this stuff is worth it, you can buy me a beer in return.             #
###############################################################################
"""

import optparse
import os

# Setup program usage
usage = """%prog SRCDATA
or:    %prog --help

SRCDATA can be any feature class that ArcGIS understands."""

parser = optparse.OptionParser(usage=usage)

parser.add_option("-t", "--translation", dest="translationMethod",
                  metavar="TRANSLATION",
                  help="Select the attribute-tags translation method. See " +
                  "the translations/ directory for valid values.")

parser.add_option("-o", "--output", dest="outputFile", metavar="OUTPUT",
                  help="Set destination .osm file name and location.")

parser.add_option("-v", "--verbose", dest="verbose", action="store_true")

parser.add_option("-d", "--debug-tags", dest="debugTags", action="store_true",
                  help="Output the tags for every feature parsed.")

parser.add_option("-f", "--force", dest="forceOverwrite", action="store_true",
                  help="Force overwrite of output file.")

parser.add_option("-m", "--merge-nodes", dest="mergeNodes",
                  action="store_true",
                  help="If there are multiple point features within " +
                       "rounding distance of each other, then arbitrarily " +
                       "ignore all but one.")

parser.add_option("-w", "--merge-ways", dest="mergeWayNodes",
                  action="store_true",
                  help="If adjacent vertices in a feature are within " +
                       "rounding distance of one another then generalize " +
                       "the line by omitting the 'redundant' vertices.")

parser.add_option("-c", "--output-change", dest="outputChange",
                  action="store_true",
                  help="Create an OSM Change file instead of a JOSM file.")

# Add timestamp attributes. This can cause big problems so surpress the help
parser.add_option("--add-timestamp", dest="addTimestamp", action="store_true",
                  help=optparse.SUPPRESS_HELP)

parser.add_option("--significant-digits", dest="significantDigits", type=int,
                  help="Number of decimal places for coordinates. " +
                  "Defaults to 9.", default=9)

parser.add_option("--rounding-digits", dest="roundingDigits", type=int,
                  help="Number of decimal places for rounding. " +
                  "Defaults to 7.", default=7)

parser.add_option("--id", dest="id", type=int,
                  help="ID to start counting from for the output file. " +
                       "Defaults to 0.", default=0)

parser.add_option("--changeset-id", dest="changesetId", type=int,
                  help="Sentinal ID number for the changeset.  Only used " +
                       "when an osmChange file is being created. " +
                       "Defaults to -1.", default=-1)

parser.set_defaults(translationMethod=None, outputFile=None,
                    verbose=False, debugTags=False, forceOverwrite=False,
                    mergeNodes=False, mergeWayNodes=False, outputChange=False,
                    addTimestamp=False)

# Parse and process arguments
(options, args) = parser.parse_args()

if len(args) < 1:
    parser.error(u"You must specify a source feature class.")
elif len(args) > 1:
    parser.error(u"You have specified too many arguments. " +
                 u"Only supply the source feature class.")

# Input and output file
options.sourceFile = args[0]
# if no output file given, use the basename of the source but with .osm
if options.outputFile is not None:
    options.outputFile = os.path.realpath(options.outputFile)
elif not os.path.exists(options.sourceFile):
    parser.error(u"An output file must be explicitly specified " +
                 u"when using a database source.")
else:
    (base, ext) = os.path.splitext(os.path.basename(options.sourceFile))
    options.outputFile = os.path.join(os.getcwd(), base + ".osm")

if not options.forceOverwrite and os.path.exists(options.outputFile):
    parser.error(
        u"Output file '{0:s}' exists".format(options.outputFile))


from arc2osmcore import makeosmfile
makeosmfile(options)
