# The config files are generated from the specifications in two internal NPS Google Sheets:
# https://docs.google.com/spreadsheets/d/1V8DsAeBipMrll2rmjjTZ6fYTE8g69dI9k6V762K4PYA
# https://docs.google.com/spreadsheets/d/1XFqkmIYMEp73q9flgNto9QJim6N5hbacgkUAgdf0rhE
# The sheets are parsed and the config_*.py files are generated with build_configs.py

# with ogr2osm, the GIS field names are case sensitive
# with arc2osm, all GIS field names are converted to lower case
# all OSM/Places tags should be lower case

# All config files must have 4 dictionaries: defaults, fieldmap, altnames and valuemap

# tags assigned to all features processed by this translator
defaults = {
    # 'key: 'value'
}

# the fieldmap maps an unaltered value from GIS field name to Places tag
# the GIS field name is guaranteed to be unique (hash table), but not the places tag
# if the same tag is used in multiple dictionary entries, there is no telling which value
# will be stored in that tag since the items in a dictionary are unsorted.
fieldmap = {
    # GIS_FieldName : Places Tag
}

# alternate GIS field names.
# The keys in this dictionary are the canonical names of GIS fields, and the associated list
# are all the alternative spellings for the same field.  The fieldmap and valuemap dictionaries
# are defined in terms of the canonical GIS field name.  If the canonical GIS field name does
# not exist, then the first field found from the alternative spellings is used.
altnames = {
    # GIS Standard FieldName: List of alternate spellings of field name
}

# the valuemap maps specific values in specific fields to a set of Places Tags
valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
}
