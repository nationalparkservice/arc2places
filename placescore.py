import arcpy
import utils


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
    # print results
    return results


# TODO - Maybe this should be a method on the Translator (different versions for arc and ogr)
def valid4upload(featureclass, places, translator=None):

    """
    Checks if a feature class is suitable for uploading to Places.

    Requires arcpy and ArcGIS 10.x ArcView or better license

        Checks for Upload:
        * Geometry: polys, lines, point, no multipoints, patches, etc
        * Must have a spatial reference system
        * Do feature, vertex, and max vertex/feature counts, and verify below api capabilities
        * No multilines (multipolys are ok)

    :rtype : List (of basestring)
    :param featureclass: The ArcGIS feature class to validate
    :param places: A Places object (needed for places connection info)
    :param translator: a Translator object (used to filter the featureclass)
    :return: empty list (or None) if there are not issues (ok to upload)
             returns list of issues (strings) that preculde upload.
             method will try to return as many issues as possible.
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
        issue = 'Some features have too many (' + max_waynodes + '+) vertices. OIDs: '
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


def valid4sync(featureclass, translator=None):

    """
    Checks if a feature class is suitable for syncing with Places.

    Requires arcpy and ArcGIS 10.x ArcView or better license

        Assumes but does not check that feature is suitable for Upload
        Additional checks for Syncing:
        * Check that geometryid is fully populated and unique (otherwise sync will not work)
        * must support editor tracking (geodatabase)

    :rtype : List (of basestring)
    :param featureclass: The ArcGIS feature class to validate
    :param translator: a Translator object (used to filter the featureclass)
    :return: An empty list if there are no issues (suitable for syncing)
             returns list of issues (strings) that preculde syncing.
             method will try to return as many issues as possible.
    """

    # TODO - Implement
    return [featureclass, translator]


# TODO: rename and implement add/populate GEOMETRYID
def init4places(featureclass, quiet=False):

    """
    Sets up a Geodatabase feature class for syncing with Places.

    Adds a PlacesID column if it doesn't exist,
    turn on archiving if not already on.

    :rtype : bool
    :param featureclass: The ArcGIS feature class to validate
    :param quiet: Turns off all messages
    :return: True if successful, False otherwise

    """

    if not featureclass:
        if not quiet:
            utils.error("No feature class provided.")
        return False

    if not arcpy.Exists(featureclass):
        if not quiet:
            utils.error("Feature class not found.")
        return False

    # FIXME: Implement
    return True


def add_places_ids(featureclass, linkfile, id_name='GEOMETRYID',
                   places_name='PLACESID', id_name_link='GEOMETRYID',
                   places_name_link='PLACESID', quiet=False):

    """
    Populates the PlacesId in an EGIS dataset.

    Populates the places_name column in featureclass using the CSV linkfile
    returned after uploading an OsmChange file.

    :rtype : bool
    :param featureclass: The ArcGIS feature class to validate
    :param linkfile: an ArcGIS dataset path to a table with Places Ids linked to EGIS Ids
    :param id_name: The name of the EGIS ID column in the feature class
    :param places_name:  The name of the Places ID column in the feature class
    :param id_name_link: The name of the EGIS ID column in the CSV file
    :param places_name_link:  The name of the Places ID column in the CSV
    :param quiet: Turns off all messages
    :return: True if successful, False otherwise

    """

    if not featureclass:
        if not quiet:
            utils.error("No feature class provided.")
        return False

    if not arcpy.Exists(featureclass):
        if not quiet:
            utils.error("Feature class not found.")
        return False

    # TODO - check that both datasets have table properties (use arcpy.Describe)

    if not linkfile:
        if not quiet:
            utils.error("No link file provided.")
        return False

    if not arcpy.Exists(linkfile):
        if not quiet:
            utils.error("Link file not found.")
        return False

    if not utils.hasfield(featureclass, id_name):
        if not quiet:
            utils.error("Field '{0:s}' not found in feature class."
                        .format(id_name))
        return False

    if not utils.hasfield(featureclass, places_name):
        if not quiet:
            utils.error("Field '{0:s}' not found in feature class."
                        .format(places_name))
        return False

    if not utils.hasfield(linkfile, id_name_link):
        if not quiet:
            utils.error("Field '{0:s}' not found in Link file."
                        .format(id_name_link))
        return False

    if not utils.hasfield(linkfile, places_name_link):
        if not quiet:
            utils.error("Field '{0:s}' not found in Link file."
                        .format(places_name_link))
        return False

    # We will have a dst_type, because we verified the field exists
    dst_type = utils.fieldtype(featureclass, places_name)
    if dst_type not in ['double', 'integer', 'string']:
        if not quiet:
            utils.error("Field '{0:s}' in feature class is not a valid type."
                        .format(places_name))
        return False

    table_view = arcpy.MakeTableView_management(featureclass, "view")
    view_name = arcpy.Describe(table_view).basename
    join_name = arcpy.Describe(linkfile).basename
    dst = view_name + "." + places_name
    src = join_name + "." + places_name_link
    try:
        arcpy.AddJoin_management(table_view, id_name, linkfile, id_name_link)
        if dst_type == 'double':
            arcpy.CalculateField_management(table_view,
                                            dst, 'float(!' + src + '!)')
        if dst_type == 'integer':
            arcpy.CalculateField_management(table_view,
                                            dst, 'int(!' + src + '!)')
        if dst_type == 'string':
            arcpy.CalculateField_management(table_view,
                                            dst, 'str(!' + src + '!)')
    # TODO - could fail if table_view/featureclass is not writable
    finally:
        arcpy.Delete_management(table_view)
    return True


def test():
    import OsmApiServer
    from Translator import Translator
    server = OsmApiServer.Places()
    sde = 'Database Connections/akr_facility_on_inpakrovmais_as_domainuser.sde'
    test_list = [('./tests/test.gdb/roads_ln', 'roads'),
                 ('./tests/test.gdb/trails_ln', 'trails'),
                 ('./tests/test.gdb/multipoints', 'generic'),
                 ('./tests/test.gdb/parkinglots_py', 'parkinglots'),
                 ('./tests/test.gdb/poi_pt', 'poi'),
                 ('./tests/test.gdb/trails_ln', 'none'),
                 (sde + '/akr_facility.GIS.TRAILS_ln', 'trails'),  # crashes python due to ArcGIS bug in da.cursor
                 (sde + '/akr_facility.GIS.ROADS_ln', 'roads')
                 ]
    for src, tname in test_list:
        print '**** Testing', src, 'with', tname
        translator = Translator.get_translator(tname)
        print valid4upload(src, server, translator)
        # print valid4sync(src, translator)


if __name__ == '__main__':
    test()
