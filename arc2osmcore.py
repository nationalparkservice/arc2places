#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" arc2osm beta

This ArcToolbox Tool takes an esri featureclass and outputs an OSM file
with that data.

By default tags will be naively copied from the input data. Hooks are provided
so that, with a little python programming, you can translate the tags however
you like. More hooks are provided so you can filter or even modify the features
themselves.

To use the hooks, create a file in the translations/ directory called myfile.py
and run agr2osm.py <featureclass> <outfile.osm> myfile. This file should define
a function with the name of each hook you want to use. Hooks are 'filterTags',
'filterFeature', 'filterFeaturePost', and 'preOutputTransform'.

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

import sys
import os
import arcpy

import utils
from geom import *


def loadtranslations(options):
    translator = options.translationMethod
    defautltranslations = {
        'filterTags': lambda tags: tags,
        'filterFeature':
            lambda arcfeature, fieldnames, reproject: arcfeature,
        'filterFeaturePost':
            lambda feature, arcfeature, arcgeometry: feature,
        'preOutputTransform': lambda geometries, features: None
    }
    newtranslations = {}
    translationmodule = None

    if translator:
        # add dirs to path if necessary
        (root, ext) = os.path.splitext(translator)
        if os.path.exists(translator) and ext == '.py':
            # user supplied translation file directly
            sys.path.insert(0, os.path.dirname(root))
        else:
            # first check translations in the subdir translations of cwd
            sys.path.insert(0, os.path.join(os.getcwd(), "translations"))
            # then check subdir of script dir
            sys.path.insert(1, os.path.join(os.path.dirname(__file__),
                                            "translations"))
            # (the cwd will also be checked implicitly)

        # strip .py if present, as import wants just the module name
        if ext == '.py':
            translator = os.path.basename(root)

        try:
            translationmodule = __import__(translator, fromlist=[''])
        except ImportError:
            utils.die(
                u"Could not load translation method '{0:s}'. Translation "
                u"script must be in your current directory, or in the "
                u"'translations' subdirectory of your current or "
                u"arc2osmcore.py directory. The following directories have "
                u"been considered: {1:s}"
                .format(translator, str(sys.path)))
        except SyntaxError as e:
            utils.die(
                u"Syntax error in '{0:s}'."
                "Translation script is malformed:\n{1:s}"
                .format(translator, e))
        if options.verbose and translationmodule:
            utils.info(
                u"Successfully loaded '{0:s}' translation method ('{1:s}')."
                .format(translator,
                        os.path.realpath(translationmodule.__file__)))
    else:
        if options.verbose:
            utils.info("Using default translations")

    for k in defautltranslations:
        if hasattr(translationmodule, k) and getattr(translationmodule, k):
            newtranslations[k] = getattr(translationmodule, k)
            if options.verbose:
                utils.info("Using user " + k)
        else:
            newtranslations[k] = defautltranslations[k]
            if options.verbose and not translator:
                utils.info("Using default " + k)
    return newtranslations


def parsedata(options):
    src = options.sourceFile
    if not arcpy.Exists(src):
        utils.die(u"Data source '{0:s}' is not recognized by ArcGIS"
                  .format(src))
    shapefield = arcpy.Describe(src).shapeFieldName
    fieldnames = ['Shape@'] + \
                 [f.name for f in arcpy.ListFields(src) if
                  f.name != shapefield]
    sr = arcpy.SpatialReference(4326)  # WGS84
    featurefilter = options.translations['filterFeature']
    with arcpy.da.SearchCursor(src, fieldnames, None, sr) as cursor:
        for arcfeature in cursor:
            feature = featurefilter(arcfeature, fieldnames, None)
            parsefeature(feature, fieldnames, options)


def parsefeature(arcfeature, fieldnames, options):
    if not arcfeature:
        return
    # rely on parsedata() to put the shape at the beginning of the list
    arcgeometry = arcfeature[0]
    if not arcgeometry:
        return
    geometries = parsegeometry([arcgeometry], options)

    featurefilter = options.translations['filterFeaturePost']
    for geometry in geometries:
        if geometry is None:
            return

        feature = Feature()
        feature.tags = getfeaturetags(arcfeature, fieldnames, options)
        feature.geometry = geometry
        geometry.addparent(feature)

        featurefilter(feature, arcfeature, arcgeometry)


def getfeaturetags(arcfeature, fieldnames, options):
    """
    This function builds up a dictionary with the source data attributes and
    passes them to the filterTags function, returning the result.
    """
    tags = {}
    tagfilter = options.translations['filterTags']
    # skip the first field, as parsedata() put the shape there
    for i in range(len(fieldnames))[1:]:
        # arcpy returns unicode field names and field values (when text)
        # encode all values as unicode since osm only uses text
        if arcfeature[i]:
            if sys.version[0] < '3':
                # unicode command was removed in python 3.x
                tags[fieldnames[i].upper()] = unicode(arcfeature[i])
            else:
                tags[fieldnames[i].upper()] = str(arcfeature[i])
    newtags = tagfilter(tags)
    if options.debugTags:
        utils.info("Tags: " + str(newtags))
    return newtags


def parsegeometry(arcgeometries, options):
    returngeometries = []
    for arcgeometry in arcgeometries:
        geometrytype = arcgeometry.type
        # geometrytype in polygon, polyline, point, multipoint, multipatch,
        # dimension, or annotation
        if geometrytype == 'point':
            returngeometries.append(parsepoint(arcgeometry.getPart(0),
                                    options))
        elif geometrytype == 'polyline' and not arcgeometry.isMultipart:
            returngeometries.append(parselinestring(arcgeometry.getPart(0),
                                    options))
        elif geometrytype == 'polygon' and not arcgeometry.isMultipart:
            returngeometries.append(parsepolygonpart(arcgeometry.getPart(0),
                                                     options))
        elif geometrytype == 'multipoint' or geometrytype == 'polyline' \
                or geometrytype == 'polygon':
            returngeometries.extend(parsecollection(arcgeometry, options))
        else:
            utils.warn("unhandled geometry, type: " + geometrytype)
            returngeometries.append(None)

    return returngeometries


def parsepoint(arcpoint, options):
    x = int(round(arcpoint.X * 10 ** options.significantDigits))
    y = int(round(arcpoint.Y * 10 ** options.significantDigits))
    geometry = Point(x, y)
    return geometry

# parselinestring is inefficient O(n^2) where n = # of vertices.
# For every vertex we need to search the
# set of existing vertices (in a hash table, but still) to get the
# "real identity" of this vertex if it exists.
# This seems necessary to ensure that "OSM topology" is obtained - there
# is only one node created when lines close of intersect

# keep track of all vertices, by (rx,ry), in the dataset.
# where (rx,ry) is the rounded coordinate as an int
vertices = {}


def parselinestring(arcpointarray, options):
    geometry = Way()
    global vertices
    for arcPoint in arcpointarray:
        (x, y) = (arcPoint.X, arcPoint.Y)
        (rx, ry) = (int(round(x * 10 ** options.roundingDigits)),
                    int(round(y * 10 ** options.roundingDigits)))
        if (rx, ry) in vertices:
            mypoint = vertices[(rx, ry)]
        else:
            (x, y) = (int(round(x * 10 ** options.significantDigits)),
                      int(round(y * 10 ** options.significantDigits)))
            mypoint = Point(x, y)
            vertices[(rx, ry)] = mypoint
        geometry.points.append(mypoint)
        mypoint.addparent(geometry)
    return geometry


def parsepolygonpart(arcpointarray, options):
    # Outer and inner rings are separated by null points in array
    # the first ring is the outer, and the rest are inner.
    outer = []  # a list of points
    inners = []  # a list of lists of points
    current = outer
    for pnt in arcpointarray:
        if pnt:
            current.append(pnt)
        else:
            # start a new list and add it to the end of the inners
            current = []
            inners.append(current)
    geometry = parselinestring(outer, options)
    if inners:
        exterior = geometry
        geometry = Relation()
        exterior.addparent(geometry)
        geometry.members.append((exterior, "outer"))
        for inner_ring in inners:
            interior = parselinestring(inner_ring, options)
            interior.addparent(geometry)
            geometry.members.append((interior, "inner"))
    return geometry


def parsecollection(arcgeometry, options):
    """
    :param arcgeometry: is an arcpy.Geometry object (of various compound types)
    :return: a list of geom.Relations
    """

    geometrytype = arcgeometry.type
    if geometrytype == 'polygon':
        # multipolygon (I already got the single part polygon in parsegeometry)
        geometries = []
        for polygon in range(arcgeometry.partCount):
            geometries.append(parsepolygonpart(arcgeometry.getPart(polygon),
                                               options))
        return geometries  # list of Relations
    elif geometrytype == 'polyline':
        # multipolyline (single part polyline handled in parsegeometry)
        geometries = []
        for linestring in range(arcgeometry.partCount):
            geometries.append(parselinestring(arcgeometry.getPart(linestring),
                                              options))
        return geometries  # list of Ways
    else:
        # multipoint
        # OSM does not have a multipoint relation
        # http://wiki.openstreetmap.org/wiki/Types_of_relation
        # treat as individual nodes with the same tags
        geometries = []
        for pnt in arcgeometry:
            geometries.append(parsepoint(pnt, options))
        return geometries  # list of Points


# mergepoints seems unecessary.
# points have features (which carry the tags for geomety) as parents
# so two nodes at the same location with different tags will be merged
# the remaining node does not get a second parent (bug?), but the two
# parents point to the same node after merging.
# When output, the nodes are used to create a dictionary (node:feature},
# and by the rules of python, the last feature found for a node will be the
# one that is output.
# put another way, tags for points with similar geometry are not merged,
# rather one is arbitrarily ignored
# either the tags should be merged (values for duplicate keys should be
# concatenated?) or all points should be output, even if the geometry
# is the same.
def mergepoints(options):
    """
    From all the nodes we have created, remove those that are duplicate (by
    comparing location up to the rounding digits). Parents of the removed
    nodes (ways and relations) are updated to reference the retained
    version of the node)
    :return: Nothing, the list of nodes is in the global state
    """
    if options.verbose:
        utils.info("Merging points")
    points = [geom for geom in Geometry.geometries if type(geom) == Point]

    # Make list of Points at each location
    if options.verbose:
        utils.info("Merging points - Making lists")
    pointcoords = {}  # lists of points for each rounded location
    # TODO make faster by keeping separate dict of dup points (key by (rx,ry))
    for i in points:
        rx = int(round(i.x * 10 ** options.roundingDigits))
        ry = int(round(i.y * 10 ** options.roundingDigits))
        if (rx, ry) in pointcoords:
            pointcoords[(rx, ry)].append(i)
        else:
            pointcoords[(rx, ry)] = [i]

    # Use list to get rid of extras
    utils.info("Merging points - Reducing lists")
    for (location, pointsatloc) in pointcoords.items():
        if len(pointsatloc) > 1:
            for point in pointsatloc[1:]:
                for parent in set(point.parents):
                    parent.replacejwithi(pointsatloc[0], point)


# mergewaypoints seems unecessary
# This method is a simple generalizer by removing vertices that are close
# (within rounding distance) of each other. Nodes in a way are already
# de-dupped during parselinestring, so a line string may have have the same
# node in non-adjacent locations (i.e. self intersecting or closed linestrings)
# or at adjacent locations (i.e. high vertex density) this method finds and
# collapses close adjacent locations into one vertex.
# This method can be skipped if we are not interested in generalizing lines
def mergewaypoints(options):
    if options.verbose:
        utils.info("Merging duplicate points in ways")
    ways = [geom for geom in Geometry.geometries if type(geom) == Way]

    # Remove duplicate points from ways,
    # a duplicate has the same id as its predecessor
    for way in ways:
        previous = options.id
        merged_points = []

        for node in way.points:
            if previous == options.id or previous != node.id:
                merged_points.append(node)
                previous = node.id

        if len(merged_points) > 0:
            way.points = merged_points


def output_file(options):
    """
    Writes an JOSM file (http://wiki.openstreetmap.org/wiki/JOSM_file_format)
    suitable for use uploading with JOSM or an osmChange file
    (see http://wiki.openstreetmap.org/wiki/OsmChange)
    suitable for use with the /api/0.6/changeset/#id/upload API
    :param options:
    :return: none
    """
    path = options.outputFile
    if not path:
        return
    '''
    Since we will be running under ArcGIS 10.x+ we will always have python 2.5+
    and xml.etree.ElementTree. However, lxml (See http://lxml.de/tutorial.html)
    should be the fastest method
    '''
    try:
        from lxml import eTree
        if options.verbose:
            utils.info("Outputting XML with lxml.etree")
    except ImportError:
        import xml.etree.ElementTree as eTree
        if options.verbose:
            utils.info("Outputting XML with ElementTree")

    # First, set up a few data structures for optimization purposes
    nodes = [geom for geom in Geometry.geometries if type(geom) == Point]
    ways = [geom for geom in Geometry.geometries if type(geom) == Way]
    relations = [geom for geom in Geometry.geometries if
                 type(geom) == Relation]
    featuresmap = {feature.geometry: feature for feature in Feature.features}

    # Open up the output file with the system default buffering
    # with open(path, 'w') as f:

    if options.outputChange:
        rootnode = eTree.Element('osmChange',
                                 {"version": "0.6", "generator": "npsarc2osm"})
        elementroot = eTree.Element('create')
        rootnode.append(elementroot)
    else:
        rootnode = eTree.Element('osm',
                                 {"version": "0.6", "generator": "npsarc2osm"})
        elementroot = rootnode

    # Build up a dict for optional settings
    attributes = {}
    # changeset and version are required for API 0.6
    if options.outputChange:
        attributes.update({'changeset': str(options.changesetId),
                           'version': '1'})
    if options.addTimestamp:
        from datetime import datetime
        attributes.update({
            'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')})

    for node in nodes:
        xmlattrs = {'visible': 'true', 'id': str(node.id),
                    'lat': str(node.y * 10 ** -options.significantDigits),
                    'lon': str(node.x * 10 ** -options.significantDigits)}
        xmlattrs.update(attributes)

        xmlobject = eTree.Element('node', xmlattrs)

        if node in featuresmap:
            for (key, value) in featuresmap[node].tags.items():
                tag = eTree.Element('tag', {'k': key, 'v': value})
                xmlobject.append(tag)

        elementroot.append(xmlobject)

    for way in ways:
        xmlattrs = {'visible': 'true', 'id': str(way.id)}
        xmlattrs.update(attributes)

        xmlobject = eTree.Element('way', xmlattrs)

        for node in way.points:
            nd = eTree.Element('nd', {'ref': str(node.id)})
            xmlobject.append(nd)
        if way in featuresmap:
            for (key, value) in featuresmap[way].tags.items():
                tag = eTree.Element('tag', {'k': key, 'v': value})
                xmlobject.append(tag)

        elementroot.append(xmlobject)

    for relation in relations:
        xmlattrs = {'visible': 'true', 'id': str(relation.id)}
        xmlattrs.update(attributes)

        xmlobject = eTree.Element('relation', xmlattrs)

        for (member, role) in relation.members:
            member = eTree.Element('member',
                                   {'type': 'way', 'ref': str(member.id),
                                    'role': role})
            xmlobject.append(member)

        tag = eTree.Element('tag', {'k': 'type', 'v': 'multipolygon'})
        xmlobject.append(tag)
        if relation in featuresmap:
            for (key, value) in featuresmap[relation].tags.items():
                tag = eTree.Element('tag', {'k': key, 'v': value})
                xmlobject.append(tag)

        elementroot.append(xmlobject)
    xml = eTree.ElementTree(rootnode)
    xml.write(path, encoding='utf-8', xml_declaration=True)


def makeosmfile(options):
    Geometry.elementIdCounter = options.id
    if options.verbose:
        utils.info(u"Preparing to convert '{0:s}' to '{1:s}'."
                   .format(options.sourceFile, options.outputFile))
    options.translations = loadtranslations(options)
    parsedata(options)
    if options.mergeNodes:
        mergepoints(options)
    if options.mergeWayNodes:
        mergewaypoints(options)
    options.translations['preOutputTransform'](
        Geometry.geometries, Feature.features)
    output_file(options)
    if options.verbose:
        utils.info(u"Wrote {0:d} elements to file '{1:s}'"
                   .format(Geometry.elementIdCounter, options.outputFile))


class DefaultOptions:
    sourceFile = None
    outputFile = None
    translationMethod = None
    verbose = False
    debugTags = False
    forceOverwrite = True
    mergeNodes = False
    mergeWayNodes = False
    outputChange = True
    addTimestamp = False
    roundingDigits = 7
    significantDigits = 9
    id = 0
    changesetId = -1
    translations = None


if __name__ == '__main__':
    opts = DefaultOptions
    opts.sourceFile = r"C:\tmp\places\test.gdb\PARKINGLOTS_py"
    opts.outputFile = r"C:\tmp\places\test_parking.osm"
    opts.translationMethod = "parkinglots"
    makeosmfile(opts)
