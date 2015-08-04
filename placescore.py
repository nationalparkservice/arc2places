import arcpy
import utils

# TODO: entire module is dependent on arcpy, develop ogr version
# TODO: develop command line versions of functions called by toolbox.
# TODO: Add tests for add_uniqueid_field() and populate_related_field()


def get_feature_info(featureclass, translator=None):
    """
    Internal method to count the features and vertices in a polyline, polygon featureclass
    :param featureclass: a polyline or polygon feature class to count
    :param translator: is an instance of the Translator class it is used to filter the featureclass
    :return: List of (oid, List of vertex_count_per_part) tuples, one for each feature.
    vertex_count_per_part, is the number of vertices in a single part of the feature
    """
    results = []
    # The default shape format with da.cursor is centroid, I need the full geometry with 'SHAPE@'
    shape_field_name = arcpy.Describe(featureclass).shapeFieldname
    oid_field_name = arcpy.Describe(featureclass).OIDFieldName
    fieldnames = [f.name for f in arcpy.ListFields(featureclass)]
    is_point = arcpy.Describe(featureclass).shapeType == 'Point'
    shape_field_index = fieldnames.index(shape_field_name)
    oid_field_index = fieldnames.index(oid_field_name)
    cursor = arcpy.SearchCursor(featureclass, fields=";".join(fieldnames))
    if cursor:
        for row in cursor:
            arcfeature = [row.getValue(fn) for fn in fieldnames]
            # print arcfeature
            if translator:
                feature = translator.filter_feature(arcfeature, fieldnames, None)
            else:
                feature = arcfeature
            if feature:
                oid = feature[oid_field_index]
                if is_point:
                    results.append((oid, [1]))
                else:
                    shape = feature[shape_field_index]
                    # print oid, shape
                    part_list = []
                    for i in range(shape.partCount):
                        vertex_array = shape.getPart(i)
                        part_list.append(len(vertex_array))
                    results.append((oid, part_list))
        del cursor
    # print results
    return results


def get_duplicates(featureclass, primary_key, translator=None):
    duplicates = {}
    shape_field_name = arcpy.Describe(featureclass).shapeFieldname
    fieldnames = [f.name for f in arcpy.ListFields(featureclass) if f != shape_field_name]
    primary_key_field_index = fieldnames.index(primary_key)
    cursor = arcpy.SearchCursor(featureclass, fields=";".join(fieldnames))
    # find primary key value frequency (filtered by translator)
    field_count = {}
    if cursor:
        for row in cursor:
            arcfeature = [row.getValue(fn) for fn in fieldnames]
            # print arcfeature
            if translator:
                feature = translator.filter_feature(arcfeature, fieldnames, None)
            else:
                feature = arcfeature
            if feature:
                key = feature[primary_key_field_index]
                if key is None:
                    key = '<Null>'
                if key in field_count:
                    field_count[key] += 1
                else:
                    field_count[key] = 1
        del cursor
    for key, value in field_count.iteritems():
        if 1 < value:
            duplicates[key] = value
    # print duplicates
    return duplicates


# Public - called by ValidateForPlaces, SeedPlaces in Places.pyt; test() in self
def valid4upload(featureclass, places, translator=None):
    """
    Checks if a feature class is suitable for uploading to Places.

    Returns as many issues as possible. Only checks the features that pass the filter in the translator.
    Requires arcpy and ArcGIS 10.x ArcView or better license
    Checks for Upload (requirements by code in arc2osm.py and API Server):
    * Geometry: polys, lines, point, no multipoints, patches, etc
    * Must have a spatial reference system
    * Do feature, vertex, and max vertex/feature counts, and verify below api capabilities
    * No multilines (multipolys are ok)

    :param featureclass: The ArcGIS feature class to validate
    :param places: A Places object (needed for places connection info)
    :param translator: a Translator object (used to filter the featureclass)
    :return: empty list (or None) if there are not issues (ok to upload)
             returns list of issues (strings) that preculde upload.
             method will try to return as many issues as possible.
    :rtype : List (of basestring)
    """
    if not featureclass:
        return ['no feature class']

    if not arcpy.Exists(featureclass):
        return ['feature class not found']

    info = arcpy.Describe(featureclass)

    if info.datasetType != 'FeatureClass':
        return ['Dataset type ' + info.datasetType + ' is not supported. Must be a FeatureClass.']

    issues = []
    if info.featureType != 'Simple':
        issues.append('Feature Type ' + info.featureType + ' is not supported. Must be Simple.')

    sr = info.spatialReference
    if not sr or sr.type not in ['Geographic', 'Projected']:
        issues.append('Feature Class must have a Geographic or Projected spatial reference system.')

    if info.shapeType not in ['Polygon', 'Polyline', 'Point']:
        issues.append('Shape Type ' + info.shapeType + ' is not supported. Must be Polygon, Polyline or Point.')
        return issues

    # The following is only dones for Polygon, Polyline and Points
    max_waynodes = places.get_max_waynodes()
    max_elements = places.get_max_elements()
    feature_list = get_feature_info(featureclass, translator)
    feature_count = len(feature_list)
    vertex_count = sum([sum(partlist) for (oid, partlist) in feature_list])
    multiparts = [oid for (oid, partlist) in feature_list if 1 < len(partlist)]
    if info.shapeType == 'Polygon':
        relation_count = len(multiparts)
        big_features = [oid for (oid, partlist) in feature_list if max_waynodes < max(partlist)]
    else:
        relation_count = 0
        if info.shapeType == 'Polyline':
            big_features = [oid for (oid, partlist) in feature_list if max_waynodes < sum(partlist)]
        else:
            big_features = []
    if big_features:
        issue = 'Some features have too many (>{0}) vertices. OIDs: '.format(max_waynodes)
        issue += ','.join([str(oid) for oid in big_features])
        issues.append(issue)
    if multiparts and info.shapeType == 'Polyline':
        issue = 'Multipart polylines are not supported. OIDs: '
        issue += ','.join([str(oid) for oid in multiparts])
        issues.append(issue)
    total = feature_count + vertex_count + relation_count
    if max_elements < total:
        issues.append('Feature class is too large ({0} features plus vertices). '
                      'Limit is {1}.'.format(total, max_elements))

    return issues


# Public - called by ValidateForPlaces, SeedPlaces in Places.pyt; test() in self
def valid4sync(featureclass, translator=None):
    """
    Checks if a feature class is suitable for syncing with Places.

    Returns as many issues as possible. Only checks the features that pass the filter in the translator.
    Requires arcpy and ArcGIS 10.x ArcView or better license.
    Assumes but does not check that featureclass is suitable for Upload
    Additional checks for Syncing (requirements by code in arcupdate2osm.py):
    * Checks that column that translates to 'nps:source_id' is fully populated and unique.
    * Checks that editor tracking is turned on and the last_edit_date_field is defined (must be a geodatabase)

    :param featureclass: The ArcGIS feature class to validate
    :param translator: a Translator object (used to filter the featureclass)
    :return: An empty list if there are no issues (suitable for syncing).
             Returns list of issues (strings) that preculde syncing.
    :rtype : List (of basestring)
    """
    if not featureclass:
        return ['no feature class']

    if not arcpy.Exists(featureclass):
        return ['feature class not found']

    info = arcpy.Describe(featureclass)

    if info.datasetType != 'FeatureClass':
        return ['Dataset type ' + info.datasetType + ' is not supported. Must be a FeatureClass.']

    issues = []

    if not info.editorTrackingEnabled:
        issues.append('Editor Tracking must be turned on for the feature class')
    else:
        if not info.editorTrackingEnabled:
            issues.append("Editor Tracking must have an 'Edit Date' field defined for the feature class")

    if translator is None:
        issues.append("Cannot validate the 'nps:source_id'.  You must provide a translator.")
        return issues

    primary_keys = translator.fields_for_tag('nps:source_id')
    field_names = [f.name for f in arcpy.ListFields(featureclass)]
    existing_keys = [k for k in primary_keys if k in field_names]
    if len(existing_keys) < 1:
        issues.append("There is no field that maps to the 'nps:source_id' tag")
    if 1 < len(existing_keys):
        issues.append("There are multiple fields {0:s} that map to the 'nps:source_id' tag".format(existing_keys))
    if len(existing_keys) == 1:
        primary_key = existing_keys[0]
        duplicates = get_duplicates(featureclass, primary_key, translator)
        if duplicates:
            issues.append("Primary key: {0:s} has duplicate values: {1:s}".format(primary_key, duplicates))

    return issues


# Public - called by AddUniqueId in Places.pyt
def add_uniqueid_field(featureclass, field_name):
    """
    Adds a 50 char text field to the featureclass and fills it with guid values.

    When called by toolbox, the input parameters have been validated.
    Other callers should check for arcpy.ExecuteError

    :param featureclass: The ArcGIS feature class to get the new field
    :param field_name: The field name to add.  Must not exist.
    :return: No return value
    :rtype : None
    """
    arcpy.AddField_management(featureclass, field_name, "TEXT", field_length=38)
    expression = "CalcGUID()"
    codeblock = """def CalcGUID():
    import uuid
    return '{' + str(uuid.uuid4()).upper() + '}'"""
    arcpy.CalculateField_management(featureclass, field_name, expression, "PYTHON_9.3", codeblock)


# Public - called by IntegratePlacesIds, SeedPlaces in Places.pyt
def populate_related_field(featureclass, linkfile, primary_key_field_name,
                           destination_field_name, foreign_key_field_name, source_field_name):
    """
    Adds values from a source table to the related records in the destination table.

    Populates the destination_field_name column in featureclass using the source_field_name in linkfile

    Raises TypeError if parameters are the wrong type
    Raises ValueError if the parameters do not have valid values
    Raises arcpy.ExecuteError if feature class is not writable
    Raises arcpy.ExecuteError if the value in src field cannot be converted to dst type

    :param featureclass: The ArcGIS feature class to update
    :param linkfile: an ArcGIS dataset path to a table with Places Ids and EGIS Ids
    :param primary_key_field_name: The name of the primary key (EGIS ID) column in the feature class
    :param destination_field_name:  The name of the destination (Places ID) column in the feature class
    :param foreign_key_field_name: The name of the foreign key (EGIS ID) column in the link table
    :param source_field_name:  The name of the source (Places ID) column in the link table
    :return: Nothing
    :rtype : None
    """

    if not isinstance(featureclass, basestring):
        raise TypeError("featureclass must be of type string")

    if not arcpy.Exists(featureclass):
        raise ValueError("featureclass not found.")

    if not hasattr(arcpy.Describe(featureclass), 'fields'):
        raise ValueError("featureclass does not have table properties")

    if not isinstance(linkfile, basestring):
        raise TypeError("linkfile must be of type string")

    if not arcpy.Exists(linkfile):
        raise ValueError("linkfile not found.")

    if not hasattr(arcpy.Describe(featureclass), 'fields'):
        raise ValueError("linkfile does not have table properties")

    if not utils.hasfield(featureclass, primary_key_field_name):
        raise ValueError("Field '{0:s}' not found in featureclass."
                         .format(primary_key_field_name))

    if not utils.hasfield(featureclass, destination_field_name):
        raise ValueError("Field '{0:s}' not found in featureclass."
                         .format(destination_field_name))

    if not utils.hasfield(linkfile, foreign_key_field_name):
        raise ValueError("Field '{0:s}' not found in linkfile."
                         .format(foreign_key_field_name))

    if not utils.hasfield(linkfile, source_field_name):
        raise ValueError("Field '{0:s}' not found in linkfile."
                         .format(source_field_name))

    # We will have a dst_type, because we verified the field exists
    dst_type = utils.fieldtype(featureclass, destination_field_name)
    if dst_type not in ['double', 'integer', 'string']:
        raise ValueError("Field '{0:s}' in featureclass is of type '{1:s}, "
                         "must be one of 'double', 'integer', or 'string'."
                         .format(destination_field_name, dst_type))

    table_view = arcpy.MakeTableView_management(featureclass, "view")
    view_name = arcpy.Describe(table_view).basename
    join_name = arcpy.Describe(linkfile).basename
    dst = view_name + "." + destination_field_name
    src = join_name + "." + source_field_name
    try:
        arcpy.AddJoin_management(table_view, primary_key_field_name, linkfile, foreign_key_field_name)
        if dst_type == 'double':
            arcpy.CalculateField_management(table_view,
                                            dst, 'float(!' + src + '!)', 'PYTHON_9.3')
        if dst_type == 'integer':
            arcpy.CalculateField_management(table_view,
                                            dst, 'int(!' + src + '!)', 'PYTHON_9.3')
        if dst_type == 'string':
            arcpy.CalculateField_management(table_view,
                                            dst, 'str(!' + src + '!)', 'PYTHON_9.3')
    finally:
        arcpy.Delete_management(table_view)
    return True


def test():
    import OsmApiServer
    from Translator import Translator
    server = OsmApiServer.OsmApiServer('test')
    sde = 'Database Connections/akr_facility_on_inpakrovmais_as_domainuser.sde'
    test_list = [('./tests/test.gdb/roads_ln', 'roads'),
                 ('./tests/test.gdb/trails_ln', 'trails'),
                 ('./tests/test.gdb/multipoints', 'generic'),
                 ('./tests/test.gdb/parkinglots_py', 'parkinglots'),
                 ('./tests/test.gdb/poi_pt', 'poi'),
                 ('./tests/test.gdb/trails_ln', 'none'),
                 ('./tests/test.gdb/trails_ln', None),
                 (sde + '/akr_facility.GIS.TRAILS_ln', 'trails'),  # crashes python due to ArcGIS bug in da.cursor
                 (sde + '/akr_facility.GIS.ROADS_ln', 'roads')
                 ]
    for src, tname in test_list:
        print '**** Testing', src, 'with', tname
        if tname is None:
            translator = None
        else:
            translator = Translator.get_translator(tname)
        print valid4upload(src, server, translator)
        print valid4sync(src, translator)


if __name__ == '__main__':
    test()
