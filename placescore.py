import arcpy


def validate(featureclass, quiet=False):

    """
    Checks if a feature class is suitable for uploading to Places.

    Requires arcpy and ArcGIS 10.x ArcView or better license

        Checks: geodatabase = good, shapefile = ok, others = fail
        geometry: polys, lines, point, no multipoints, patches, etc
        must have a spatial reference system
        geometryid (or alt) column = good othewise = ok
        if it has a placesid column it must be empty

    :rtype : basestring
    :param featureclass: The ArcGIS feature class to validate
    :param quiet: Turns off all messages
    :return: 'ok' if the feature class meets minimum requirements for upload
             'good' if the feature class is suitable for syncing
             anything else then the feature class should not be used
    """
    if not featureclass:
        if not quiet:
            arcpy.AddWarning("No feature class provided.")
        return 'no feature class'

    if not arcpy.Exists(featureclass):
        if not quiet:
            arcpy.AddWarning("Feature class not found.")
        return 'feature class not found'

    return 'ok'


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
            arcpy.AddWarning("No feature class provided.")
        return False

    if not arcpy.Exists(featureclass):
        if not quiet:
            arcpy.AddWarning("Feature class not found.")
        return False

    return True
