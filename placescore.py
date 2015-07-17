import arcpy
import utils


def validate(featureclass, quiet=False):

    """
    Checks if a feature class is suitable for uploading to Places.

    Requires arcpy and ArcGIS 10.x ArcView or better license

        Checks: geodatabase = good, shapefile = ok, others = fail
        geometry: polys, lines, point, no multipoints, patches, etc
        must have a spatial reference system
        geometryid (or alt) column = good othewise = ok
        if it has a placesid column it must be empty
        Check that geometyid is fully populated and unique (otherwise sync will not work)
        warn if there are multilines (multipolys are ok)
        Do feature, vertex, and max vertex/feature counts, and verify below api capabilities

    :rtype : basestring
    :param featureclass: The ArcGIS feature class to validate
    :param quiet: Turns off all messages
    :return: 'ok' if the feature class meets minimum requirements for upload
             'good' if the feature class is suitable for syncing
             anything else then the feature class should not be used
    """
    if not featureclass:
        if not quiet:
            utils.error("No feature class provided.")
        return 'no feature class'

    if not arcpy.Exists(featureclass):
        if not quiet:
            utils.error("Feature class not found.")
        return 'feature class not found'

    # FIXME: Implement
    return 'good'


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
                   places_name='PLACESID', id_name_csv='GEOMETRYID',
                   places_name_csv='PLACESID', quiet=False):

    """
    Populates the PlacesId in an EGIS dataset.

    Populates the places_name column in featureclass using the CSV linkfile
    returned after uploading an OsmChange file.

    :rtype : bool
    :param featureclass: The ArcGIS feature class to validate
    :param linkfile: a CSV file with Places Ids linked to EGIS Ids
    :param id_name: The name of the EGIS ID column in the feature class
    :param places_name:  The name of the Places ID column in the feature class
    :param id_name_csv: The name of the EGIS ID column in the CSV file
    :param places_name_csv:  The name of the Places ID column in the CSV
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

    if not utils.hasfield(linkfile, id_name_csv):
        if not quiet:
            utils.error("Field '{0:s}' not found in Link file."
                        .format(id_name_csv))
        return False

    if not utils.hasfield(linkfile, places_name_csv):
        if not quiet:
            utils.error("Field '{0:s}' not found in Link file."
                        .format(places_name_csv))
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
    src = join_name + "." + places_name_csv
    try:
        arcpy.AddJoin_management(table_view, id_name, linkfile, id_name_csv)
        if dst_type == 'double':
            arcpy.CalculateField_management(table_view,
                                            dst, 'float(!' + src + '!)')
        if dst_type == 'integer':
            arcpy.CalculateField_management(table_view,
                                            dst, 'int(!' + src + '!)')
        if dst_type == 'string':
            arcpy.CalculateField_management(table_view,
                                            dst, 'str(!' + src + '!)')
    finally:
        arcpy.Delete_management(table_view)
    return True
