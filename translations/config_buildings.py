# Based on the Places Data Schema revision 6 (5/18/2015)
# https://github.com/nationalparkservice/places-data/wiki/Places-Data-Schema-Guide
# with ogr2osm, the GIS field names are case sensitive
# with arc2osm, all GIS field names are converted to upper case
# all osm/Places tags should be lower case

# All config files must have defaults, fieldmap, altnames and valuemap

# default tags for buildings *polygons* in Places
defaults = {
    'building': 'yes'
}

# values map one to one from GIS field name to Places tag
fieldmap = {
    # GIS_FieldName : Places Tag
    'COMMON_NAME': 'name',
    'BUILDING_FCODE': 'nps:building_fcode',
    'ADMIN_TYPE': 'nps:admin_type',
    'FEDERAL_ENTITY_TYPE': 'nps:federal_entity_type',
    'POLYGON_NOTES': 'note',
    'BUILDING_ID': 'nps:building_id',
    'IS_SENSITIVE': 'nps:is_sensitive'
}

# alternate GIS field names.
altnames = {
    # GIS Standard FieldName: List of alternate spellings of field name
    'COMMON_NAME': ['COMMONNAME', 'NAME'],
    'BUILDING_FCODE': ['BUILDING_FCODE', 'BLDGFCODE', 'BLDG_FCODE',
                       'FCODE', 'FACILITYCODE', 'FACILITY_CODE'],
    'ADMIN_TYPE': ['ADMINTYPE', 'BLDGADMINTYPE','BUILDING_ADMIN_TYPE'],
    'FEDERAL_ENTITY_TYPE': ['FEDERALENTITYTYPE'],
    'POLYGON_NOTES': ['POLYGON_NOTES', 'NOTES'],
    'BUILDING_ID': ['BUILDINGID'],
    'IS_SENSITIVE': ['ISSENSITIVE']
}

valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
}
