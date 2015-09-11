# Based on the Places Data Schema revision 6 (5/18/2015)
# https://github.com/nationalparkservice/places-data/wiki/Places-Data-Schema-Guide
# with ogr2osm, the GIS field names are case sensitive
# with arc2osm, all GIS field names are converted to upper case
# all osm/Places tags should be lower case

# All config files must have defaults, fieldmap, altnames and valuemap

# default tags for road *lines* in Places
defaults = {
    'highway': 'road'
}

# values map one to one from field name to OSM tag
fieldmap = {
    # GIS_FieldName : Places Tag
    'RDNAME': 'nps:road_name',
    'RDALTNAME': 'nps:road_alt_name',
    'RDLABEL': 'name',
    'RDSTATUS': 'nps:road_status',
    'RDCLASS': 'nps:road_class',
    'RDSURFACE': 'surface',
    'MAINTAINER': 'nps:road_maintainer',
    'RDLANES': 'lanes',
    'ROUTEID': 'nps:route_id',
    'RTENUMBER': 'nps:route_number'
}

# alternate GIS field names.
altnames = {
    # GIS Standard FieldName: List of alternate spellings of field name
    'RDNAME': ['NAME', 'ROADNAME', 'RD_NAME', 'ROAD_NAME'],
    'RDALTNAME': ['ALTNAME', 'ROADALTNAME', 'RD_ALTNAME', 'ROAD_ALTNAME',
                  'ALTERNAME_NAME', 'ALTERNATENAME', 'ALTNAMES',
                  'ROADALTNAMES', 'RD_ALTNAMES', 'ROAD_ALTNAMES',
                  'ALTERNAME_NAMES', 'ALTERNATENAMES'],
    'RDLABEL': ['LABEL', 'ROADLABEL', 'RD_LABEL', 'ROAD_LABEL'],
    'RDSTATUS': ['STATUS', 'ROADSTATUS', 'RD_STATUS', 'ROAD_STATUS'],
    'RDCLASS': ['CLASS', 'ROADCLASS', 'RD_CLASS', 'ROAD_CLASS',
                'ADMINISTRATIVE_ROAD_CLASS'],
    'RDSURFACE': ['SURFACE', 'ROADSURFACE', 'RD_SURFACE', 'ROAD_SURFACE'],
    'MAINTAINER': ['RDMAINTAINER', 'ROADMAINTAINER', 'RD_MAINTAINER',
                   'ROAD_MAINTAINER', 'PRIMARYROADMAINTAINER',
                   'PRIMARY_ROAD_MAINTAINER'],
    'RDONEWAY': ['ONEWAY', 'ONE_WAY', 'ROADONEWAY', 'ROAD_ONE_WAY',
                 'RD_ONE_WAY'],
    'RDLANES': ['LANES', 'ROADLANES', 'RD_LANES', 'ROAD_LANES',
                'NUMBEROFLANES', 'NUMBER_OF_LANES'],

    'ROUTEID': ['ROUTE', 'ROUTE_ID', 'FHWA_NPS_ROUTE_ID'],
    'RTENUMBER': ['RTE_NUMBER', 'ROUTENUMBER', 'ROUTE_NUMBER']
}

# GIS field names where different values map to a specific set of Places tags
valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
    'RDCLASS': {
        'primary': {'highway': 'primary'},
        'secondary': {'highway': 'secondary'},
        'local': {'highway': 'residential'},
        '4wd': {'highway': 'road', '4wd_only': 'yes'},
        'service': {
            'highway': 'service',
            'access': 'private'
        },
        'private': {'highway': 'road', 'access': 'private'}
    },
    'RDSTATUS': {
        'decommissioned': {'access': 'no'},
        'existing': {'access': 'yes'},
        'temporarily closed': {'access': 'no'},
        'proposed': {
            'access': 'no',
            'highway': 'proposed'  # conflict with RDCLASS see roads.py for resolution
        },
        'planned': {
            'access': 'no',
            'highway': 'proposed'  # conflict with RDCLASS see roads.py for resolution
        }
    },
    'RDSURFACE': {
        # *: {'surface': *}  # by fieldmap
        'asphalt': {'surface': 'asphalt'},
        'brick/pavers': {'surface': 'paving_stones'},
        'cobblestone': {'surface': 'cobblestone'},
        'concrete': {'surface': 'concrete'},
        'gravel': {'surface': 'gravel'},
        'paved other': {'surface': 'paved'},
        'sand': {'surface': 'sand'},
        'unpaved other': {'surface': 'unpaved'},
        'native or dirt': {'surface': 'ground'}
    },
    'RDONEWAY': {
        'with digitized': {'oneway': 'yes'},
        'against digitized': {'oneway': '-1'}
    }
}
