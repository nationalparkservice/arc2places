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
import arcpy

from geom import *
from Translator import Translator
from Logger import Logger

# TODO: refactor to make ogr/arc replacable
# TODO: refactor to allow modular calls with from update process


def parsedata(options):
    src = options.sourceFile
    if not arcpy.Exists(src):
        raise ValueError(u"Data source '{0:s}' is not recognized by ArcGIS".format(src))
    shapefield = arcpy.Describe(src).shapeFieldName
    fieldnames = ['SHAPE@WKT'] + \
                 [f.name for f in arcpy.ListFields(src) if
                  f.name != shapefield]
    sr = arcpy.SpatialReference(4326)  # WGS84
    with arcpy.da.SearchCursor(src, fieldnames, None, sr) as cursor:
        for arcfeature in cursor:
            feature = options.translator.filter_feature(arcfeature, fieldnames, None)
            parsefeature(feature, fieldnames, options)


def parsefeature(arcfeature, fieldnames, options):
    if not arcfeature:
        return
    # rely on caller to put the shape at the beginning of the list
    geometry = arcfeature[0]
    if geometry is None:
        return

    feature = Feature()
    feature.tags = getfeaturetags(arcfeature, fieldnames, options)
    feature.geometry = geometry.replace('NAN','0')
    # options.translator.filter_feature_post(feature, arcfeature, geometry)


def getfeaturetags(arcfeature, fieldnames, options):
    """
    This function builds up a dictionary with the source data attributes and
    passes them to the filterTags function, returning the result.
    """
    tags = {}
    # skip the first field, as parsedata() put the shape there
    for i in range(len(fieldnames))[1:]:
        # arcpy returns unicode field names and field values (when text)
        # encode all values as unicode since osm only uses text
        if arcfeature[i]:
            if sys.version[0] < '3':
                # unicode command was removed in python 3.x
                tags[fieldnames[i].lower()] = unicode(arcfeature[i])
            else:
                tags[fieldnames[i].lower()] = str(arcfeature[i])
        else:
            tags[fieldnames[i].lower()] = None
    newtags = options.translator.filter_tags(tags)
    try:
        options.logger.debug("Tags: " + str(newtags))
    except AttributeError:
        pass
    return newtags


def get_pk_name(options, places_key):
    try:
        primary_keys = options.translator.fields_for_tag(places_key)
    except AttributeError:
        return None
    field_names = [f.name for f in arcpy.ListFields(options.sourceFile)]
    # need to do case insensitive compare, but return the original case.
    # use the first value from primary_keys, not the first value from field_names.
    lower_field_names = [f.lower() for f in field_names]
    primary_key = None
    for key in primary_keys:
        if key in lower_field_names:
            primary_key = field_names[lower_field_names.index(key)]
            break
    return primary_key


def export_to_sqlserver(options):
    try:
        import pyodbc
    except ImportError:
        pyodbc = None
        print 'pyodbc module not found, make sure it is installed with'
        print 'C:\Python27\ArcGIS10.3\Scripts\pip.exe install pyodbc'
        sys.exit()

    def get_connection_or_die():
        conn_string = ("DRIVER={{SQL Server Native Client 10.0}};"
                       "SERVER={0};DATABASE={1};Trusted_Connection=Yes;")
        conn_string = conn_string.format('inpakrovmais', 'animal_movement')
        try:
            connection = pyodbc.connect(conn_string)
        except pyodbc.Error as e:
            print("Rats!!  Unable to connect to the database.")
            print("Make sure your AD account has the proper DB permissions.")
            print("Contact Regan (regan_sarwas@nps.gov) for assistance.")
            print("  Connection: " + conn_string)
            print("  Error: " + e[1])
            sys.exit()
        return connection

    def chunks(l, n):
        """Yield successive n-sized chunks from list l."""
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def stringify(value):
        if isinstance(value, basestring):
            return u"'{0}'".format(value.replace("'", "''"))
        if value:
            return u"'{0}'".format(value)
        return u"NULL"

    def order(feature, fields):
        tags = feature.tags
        shape = feature.geometry
        items = [stringify(tags.get(field)) for field in fields]
        return u"(" + u",".join(items) + u",geography::STGeomFromText('{0}',4326))".format(shape)

    def add_rows_to_sqlserver(connection, rows):
        # SQL Server is limited to 1000 rows in an insert
        wcursor = connection.cursor()
        dbdata = parktiles_tables_sql.get(options.translator.name)
        if dbdata is None:
            return
        table_name = dbdata[0]
        fields = dbdata[1]
        sql = u"insert into {0} ({1}, the_geom) values ".format(table_name, ','.join(fields))
        i = 0
        chunksize = 10
        for chunk in chunks(rows, chunksize):
            values = u','.join([order(row, fields) for row in chunk])
            sql2 = (sql + values).encode('utf8')
            if i == 0:
                print sql2
            i += 1
            print 'sending rows {0} to {1}...'.format((i-1)*chunksize, i*chunksize)
            try:
                wcursor.execute(sql2)
            except pyodbc.ProgrammingError as de:
                print ("Database error ocurred", de)
                print ("Unable to add these rows to the '{0}' table.".format(table_name))
                print (sql2)
                continue
            try:
                wcursor.commit()
            except Exception as de:
                print ("Database error ocurred", de)
                print ("Unable to add these rows to the '{0}' table.".format(table_name))
                print (sql2)

    conn = get_connection_or_die()
    data = Feature.features
    add_rows_to_sqlserver(conn, data)


def export_to_cartodb(options):
    try:
        from cartodb import CartoDBAPIKey, CartoDBException
    except ImportError:
        CartoDBAPIKey, CartoDBException = None, None
        print 'cartodb module not found, make sure it is installed with'
        print 'C:\Python27\ArcGIS10.3\Scripts\pip.exe install cartodb'
        sys.exit()
    import secrets_cartodb as secrets

    def execute_sql_in_cartodb(carto, sql):
        try:
            carto.sql(sql)
        except CartoDBException as ce:
            print ("CartoDB error ocurred", ce)
            print (sql)

    def chunks(l, n):
        """Yield successive n-sized chunks from list l."""
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def stringify(value):
        if isinstance(value, basestring):
            return u"'{0}'".format(value.replace("'", "''"))
        if value:
            return u"'{0}'".format(value)
        return u"NULL"

    def order(feature, fields):
        tags = feature.tags
        shape = feature.geometry
        items = [stringify(tags.get(field)) for field in fields]
        return u"(" + u",".join(items) + u",ST_GeometryFromText('{0}',4326))".format(shape)

    def add_rows_to_cartodb(connection, rows):
        # SQL Server is limited to 1000 rows in an insert
        dbdata = parktiles_tables_sql.get(options.translator.name)
        if dbdata is None:
            return
        table_name = dbdata[0]
        fields = dbdata[1]
        sql = u"insert into {0} ({1}, the_geom) values ".format(table_name, ','.join(fields))
        i = 0
        chunksize = 10
        for chunk in chunks(rows, chunksize):
            values = u','.join([order(row, fields) for row in chunk])
            sql2 = (sql + values).encode('utf8')
            if i == 0:
                print sql2
            i += 1
            print 'sending rows {0} to {1}...'.format((i-1)*chunksize, i*chunksize)
            try:
                execute_sql_in_cartodb(connection, sql2)
            except Exception as e:
                print "Unexpected exception occurred loading to CartoDB", e
                print sql2

    conn = CartoDBAPIKey(secrets.apikey, secrets.domain)
    data = Feature.features
    add_rows_to_cartodb(conn, data)


# TODO: This is a horrible public interface.  Make more specific
# Public - called by CreatePlacesUpload, SeedPlaces in arc2places.pyt; main() in arc2osm.py; test() in self
def makeosmfile(options, test=False):
    """
    Save or return (as an xml string) an OsmChange File.

    :rtype : None, or (error string, None) or (None, xml_string) on success
    :param options: a DefaultOptions() object with the input and control parameters
    :return: (basestring, basestring)
    """
    # Set/Reset/Clear the global state (list of geometries and features)
    Geometry.elementIdCounter = options.id
    Geometry.geometries = []
    Feature.features = []
    global vertices
    vertices = {}
    try:
        if options.outputFile is None:
            options.logger.info(u"Preparing to convert '{0:s}'."
                                .format(options.sourceFile))
        else:
            options.logger.info(u"Preparing to convert '{0:s}' to '{1:s}'."
                                .format(options.sourceFile, options.outputFile))
    except AttributeError:
        pass
    if not options.translator:
        try:
            options.logger.info(u"Loading translator '{0:s}'.".format(options.translationMethod))
        except AttributeError:
            pass
        translator = Translator.get_translator(options.translationMethod)
        if translator.translation_module is None:
            try:
                options.logger.error(translator.error)
            except AttributeError:
                pass
        else:
            try:
                options.logger.info(u"Successfully loaded '{0:s}' translation method ('{1:s}').".format(
                                    translator.name, translator.path))
                for function in translator.function_status:
                    options.logger.info(u"{1:s} method for function '{0:s}'".format(
                                        function, translator.function_status[function]))
            except AttributeError:
                pass
        options.translator = translator
    parsedata(options)

    if test:
        export_to_sqlserver(options)
    else:
        export_to_cartodb(options)


# Public - called by CreatePlacesUpload, SeedPlaces in arc2places.pyt; test() in self;
# noinspection PyClassHasNoInit
class DefaultOptions:
    """
    Defines the attributes expected by the sole input parameter to makeosmfile()
    """
    sourceFile = None
    outputFile = None
    translator = Translator.get_translator(None)
    logger = None
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
    datasetKey = None


parktiles_tables_sql = {
    'parktiles_poi': ('parktiles_points_of_interest', ["name", "unit_code", "type", "class", "superclass", "gis_id", "gis_updated_at", "gis_created_at", "tags", "gis_poitype"]),
    'parktiles_trails': ('parktiles_trails', ["name", "unit_code", "surface", "type", "class", "superclass", "gis_id", "gis_updated_at", "gis_created_at", "tags", "gis_trluse"]),
     # ["foot", "horse", "bicycle", "snowmobile", "motor_vehicle"
    'parktiles_roads': ('parktiles_roads', ["name", "unit_code", "description", "type", "class", "superclass", "gis_id", "gis_updated_at", "gis_created_at", "tags", "gis_rdclass"]),
    'parktiles_buildings': ('parktiles_buildings', ["name", "unit_code", "type", "class", "superclass", "gis_id", "gis_updated_at", "gis_created_at", "tags"]),
    'parktiles_parkinglots': ('parktiles_parking_lots', ["name", "unit_code", "type", "class", "superclass", "gis_id", "gis_updated_at", "gis_created_at", "tags"])
}


def test():
    import os
    opts = DefaultOptions()
    opts.logger = Logger()
    # opts.logger.start_debug()
    testdata = [
        ("parktiles_poi", os.path.join("Database Connections", "AKR_SOCIO_on_inpakrovmais_as_GIS.sde", "akr_socio.GIS.POI_pt")),
        ("parktiles_trails", os.path.abspath("./testdata/test.gdb/TRAILS_ln")),
        ("parktiles_roads", os.path.abspath("./testdata/test.gdb/ROADS_ln")),
        ("parktiles_buildings", os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde", "GIS.building_polygon")),
        ("parktiles_parkinglots", os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde", "GIS.parklots_py"))
    ]
    akrodata = [
        ("parktiles_poi", os.path.join("Database Connections", "AKR_SOCIO_on_inpakrovmais_as_GIS.sde", "akr_socio.GIS.POI_pt")),
        ("parktiles_trails", os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde", "GIS.trails_ln")),
        ("parktiles_roads", os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde", "GIS.roads_ln")),
        ("parktiles_buildings", os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde", "GIS.building_polygon")),
        ("parktiles_parkinglots", os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde", "GIS.parklots_py"))
    ]
    akro_nozm = [
        ("parktiles_trails", r"c:\tmp\test.gdb\trails"),
        ("parktiles_roads", r"c:\tmp\test.gdb\roads"),
    ]
    ncrdata = [
        ("parktiles_poi", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_POI/FeatureServer/1"),
        ("parktiles_poi", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/POHE_Places_POI/FeatureServer/1"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/0"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/1"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/2"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/3"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/4"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/5"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/6"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/7"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/8"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/9"),
        ("parktiles_trails", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Trails_Type/FeatureServer/10"),
        ("parktiles_roads", "https://inpncrofslr.nps.doi.net:6443/arcgis/rest/services/Places/NCR_Places_Roads/FeatureServer/0"),
    ]
    pwrdata = [
        ("parktiles_poi", "http://inppwcagis01:6080/arcgis/rest/services/PWR/PWR_NPS_PointsOfInterest/FeatureServer/0"),
        ("parktiles_trails", "http://inppwcagis01:6080/arcgis/rest/services/PWR/PWR_NPSTrails/FeatureServer/0"),
        ("parktiles_roads", "http://inppwcagis01:6080/arcgis/rest/services/PWR/PWR_Roads_Service/FeatureServer/0"),
    ]
    pwrdata_sde = [
        ("parktiles_poi", os.path.join("Database Connections", "PWR_as_domainuser.sde", "akr_socio.GIS.POI_pt")),
        ("parktiles_trails", os.path.join("Database Connections", "PWR_as_domainuser.sde", "akr_socio.GIS.POI_pt")),
        ("parktiles_roads", os.path.join("Database Connections", "PWR_as_domainuser.sde", "akr_socio.GIS.POI_pt"))
    ]
    for name, source in akro_nozm[0:2]:
        if source.startswith("http"):
            print "loading", source, "..."
            url = source + '/query?where=1=1&outFields=*&returnGeometry&f=json'
            source = arcpy.FeatureSet()
            try:
                source.load(url)
            except Exception as e:
                print "Unexpected exception", e
                continue
            print "done loading..."
        opts.sourceFile = source
        opts.translator = Translator.get_translator(name)
        opts.datasetKey = get_pk_name(opts, 'gis_id')
        makeosmfile(opts, test=False)


if __name__ == '__main__':
    test()
