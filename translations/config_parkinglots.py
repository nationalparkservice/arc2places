# Based on the Places Data Schema revision 6 (5/18/2015)
# https://github.com/nationalparkservice/places-data/wiki/Places-Data-Schema-Guide
# with ogr2osm, the GIS field names are case sensitive
# with arc2osm, all GIS field names are converted to upper case
# all osm/Places tags should be lower case

# All config files must have defaults, fieldmap, altnames and valuemap

# default tags for Parking *polygons* in Places
defaults = {
    'amenity': 'parking',
    'area': 'yes'
}

# values map one to one from GIS field name to Places tag
fieldmap = {
    # GIS_FieldName : Places Tag
    'LOTLABEL': 'name',
    'LOTNAME': 'nps:parkinglot_name',
    'LOTALTNAME': 'nps:parkinglot_alt_name',
    'LOTFEATTYPE': 'nps:parkinglot_feature_type',
    'LOTTYPE': 'nps:parkinglot_type'
}

# alternate GIS field names.
altnames = {
    # GIS Standard FieldName: List of alternate spellings of field name
    'LOTLABEL': ['LABEL', 'LOT_LABEL', 'NAME', 'LOTNAME', 'LOT_NAME'],
    'LOTNAME': ['NAME', 'LOT_NAME'],
    'LOTALTNAME': ['ALTNAME', 'ALT_NAME', 'LOT_ALT_NAME',
                   'ALTERNAME_NAME', 'ALTERNATENAME', 'LOT_ALTERNAME_NAME', 'LOTALTERNATENAME',
                   'ALTNAMES', 'ALT_NAMES', 'LOT_ALT_NAMES',
                   'ALTERNAME_NAMES', 'ALTERNATENAMES', 'LOT_ALTERNAME_NAMES', 'LOTALTERNATENAMES'],
    'LOTFEATTYPE': ['FEATTYPE', 'FEAT_TYPE', 'LOT_FEAT_TYPE',
                    'FEATURETYPE', 'FEATURE_TYPE', 'LOT_FEATURE_TYPE'],
    'LOTTYPE': ['TYPE', 'LOT_TYPE'],
}

valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
}
