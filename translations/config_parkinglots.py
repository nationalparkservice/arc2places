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
    'NAME': 'name',
}

# alternate GIS field names.
altnames = {
    # GIS Standard FieldName: List of alternate spellings of field name
}

valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
}
