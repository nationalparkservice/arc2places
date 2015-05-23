def valueof(name, altnames, attributes, no_values=('null', 'none', 'unknown')):
    value = None
    if name in attributes:
        value = attributes[name]
    else:
        if name in altnames:
            for altname in altnames[name]:
                if altname in attributes:
                    value = attributes[altname]
    if value:
        value = value.strip()
        if value.lower() in no_values:
            value = None
    return value


def simplemap(namemap, altnames, attributes):
    tags = {}
    for gisname in namemap:
        value = valueof(gisname, altnames, attributes)
        if value:
            tagname = namemap[gisname]
            tags[tagname] = value
    return tags


def fancymap(name, altnames, attrs, tagz, valuemaps):
    tags = {}
    value = valueof(name, altnames, attrs)
    if value and value in valuemaps:
        values = valuemaps[value]
        for i in range(len(values)):
            if values[i]:
                tagname = tagz[i]
                tags[tagname] = values[i]
    return tags


# noinspection PyPep8Naming
def filterTags(attrs):
    if not attrs:
        return

    # namemap provides a mapping from the GIS field name to the places tag
    # when there is a one to one mapping of values
    # This is based on the Places Data Schema revision 6 (5/18/2015)
    # https://github.com/nationalparkservice/places-data/wiki/Places-Data-Schema-Guide
    # with ogr2osm, the column names are case sensitive
    # with arc2osm, all column names are converted to upper case
    # all osm/places tags should be lower case

    namemap = {
        # 'EGIS_COLUMN_NAME' : 'osm/places tag name'
        # 'PLACESID': 'nps:places_id'  # Ignore - managed by system
        'UNITCODE': 'nps:unit_code',
        'UNITNAME': 'nps:unit_name',
        'GROUPCODE': 'nps:group_code',
        'REGIONCODE': 'nps:region_code',
        'LOCATIONID': 'nps:location_id',
        'ASSETID': 'nps:asset_id',
        'ISEXTANT': 'nps:is_extant',
        'MAPMETHOD': 'nps:map_method',
        'MAPSOURCE': 'source',
        'SOURCESCALE': 'nps:source_scale',
        'SOURCEDATE': 'nps:source_date',
        'XYERROR': 'nps:xy_error',
        'NOTES': 'note',
        'RESTRICTION': 'nps:restriction',
        'DISTRIBUTE': 'nps:distribute',
        'CREATEDATE': 'nps:create_date',
        'CREATEUSER': 'nps:create_user',
        'EDITDATE': 'nps:edit_date',
        'EDITUSER': 'nps:edit_user',
        'FEATUREID': 'nps:feature_id',
        'GEOMETRYID': 'nps:source_id',
        # helpful aliases
        'NAME': 'name'
    }

    alt_names = {
        'UNITCODE': ['UNIT_CODE'],
        'UNITNAME': ['UNIT_NAME'],
        'GROUPCODE': ['GROUP_CODE'],
        'REGIONCODE': ['REGION_CODE'],
        'LOCATIONID': ['LOCATION_ID', 'FMSSID', 'FMSS_ID'],
        'ASSETID': ['ASSET_ID'],
        'ISEXTANT': ['IS_EXTANT'],
        'MAPMETHOD': ['MAP_METHOD'],
        'MAPSOURCE': ['MAP_SOURCE'],
        'SOURCESCALE': ['SOURCE_SCALE'],
        'SOURCEDATE': ['SOURCE_DATE'],
        'XYERROR': ['XY_ERROR'],
        'CREATEDATE': ['CREATE_DATE', 'CREATED_DATE'],
        'CREATEUSER': ['CREATE_USER', 'CREATED_USER'],
        'EDITDATE': ['EDIT_DATE', 'LAST_EDIT_DATE', 'LAST_EDITED_DATE'],
        'EDITUSER': ['EDIT_USER', 'LAST_EDIT_USER', 'LAST_EDITED_USER'],
        'FEATUREID': ['FEATURE_ID'],
        'GEOMETRYID': ['GEOMETRY_ID'],
    }

    return simplemap(namemap, alt_names, attrs)
