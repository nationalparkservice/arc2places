# Based on the Places Data Schema revision 6 (5/18/2015)
# https://github.com/nationalparkservice/places-data/wiki/Places-Data-Schema-Guide
# with ogr2osm, the GIS field names are case sensitive
# with arc2osm, all GIS field names are converted to upper case
# all osm/Places tags should be lower case

# All config files must have defaults, fieldmap, altnames and valuemap

# default tags for trail *lines* in Places
defaults = {
    'highway': 'path',
    'horse': 'no',
    'bicycle': 'no',
    'motorcycle': 'no',
    'atv': 'no',
    'snowmobile': 'no'
}

# values map one to one from field name to OSM tag
fieldmap = {
    # GIS_FieldName : Places Tag
    'TRLNAME': 'name',
    'TRLALTNAMES': 'nps:trail_alt_names',
    'TRLFEATTYPE': 'nps:trail_feat_type',
    'TRLSTATUS': 'nps:trail_status',
    'TRLTYPE': 'nps:trail_type',
    'TRLCLASS': 'tracktype',
    'TRLUSES': 'nps:trail_uses'
}

# alternate GIS field names.
altnames = {
    # GIS Standard FieldName: List of alternate spellings of field name
    'TRLNAME': ['NAME', 'TRAILNAME', 'TRL_NAME', 'TRAIL_NAME'],
    'TRLALTNAME': ['ALTNAME', 'TRAILALTNAME', 'TRL_ALTNAME', 'TRAIL_ALTNAME',
                   'TRLALTNAMES', 'ALTNAMES', 'TRAILALTNAMES', 'TRL_ALTNAMES',
                   'TRAIL_ALTNAMES'],
    'TRLLABEL': ['LABEL', 'TRAILLABEL', 'TRL_LABEL', 'TRAIL_LABEL'],
    'TRLFEATTYPE': ['FEATTYPE', 'FEATURETYPE', 'FEATURE_TYPE', 'TRL_FEAT_TYPE',
                    'TRAILFEATURETYPE', 'TRAIL_FEATURE_TYPE'],
    'TRLSTATUS': ['STATUS', 'TRAILSTATUS', 'TRL_STATUS', 'TRAIL_STATUS'],
    'TRLSURFACE': ['SURFACE', 'TRAILSURFACE', 'TRL_SURFACE', 'TRAIL_SURFACE'],
    'TRLTYPE': ['TYPE', 'TRAILTYPE', 'TRL_TYPE', 'TRAIL_TYPE'],
    'TRLCLASS': ['CLASS', 'TRAILCLASS', 'TRL_CLASS', 'TRAIL_CLASS'],
    'TRLUSE': ['USE', 'TRAILUSE', 'TRL_USE', 'TRAIL_USE', 'USES', 'TRAILUSES',
               'TRL_USES', 'TRAIL_USES']
}

# GIS field names where different values map to a specific set of Places tags
valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
    'TRLFEATTYPE': {
        'Park Trail Centerline': {
            'highway': 'path'
        },
        'Sidewalk Centerline': {
            'highway': 'footway',
            'footway': 'sidewalk'
        }
    },
    'TRLCLASS': {
        'Trail Class 1: Minimally Developed': {'tracktype': 'grade5'},
        'Trail Class 2: Moderately Developed': {'tracktype': 'grade4'},
        'Trail Class 3: Developed': {'tracktype': 'grade3'},
        'Trail Class 4: Highly Developed': {'tracktype': 'grade2'},
        'Trail Class 5: Fully Developed': {'tracktype': 'grade1'}
    },
    'TRLUSE': {
        'Hiker/Pedestrian': {
            'highway': 'path',
            'foot': 'yes'
        },
        'Pack and Saddle': {
            'highway': 'track',
            'horse': 'yes'
        },
        'Bicycle': {
            'highway': 'track',
            'bicycle': 'yes'
        },
        'Motorcycle': {
            'highway': 'track',
            'motorcycle': 'yes'
        },
        'All-Terrain Vehicle': {
            'highway': 'track',
            'atv': 'yes'
        },
        'Four-Wheel Drive Vehicle > 50" in Tread Width': {
            'highway': 'track',
            '4wd_only': 'yes'
        },
        'Cross-Country Ski': {
            'highway': 'path',
            'piste:type': 'nordic'
        },
        'Downhill Ski': {
            'highway': 'path',
            'piste:type': 'downhill'
        },
        'Dog Sled': {
            'highway': 'track',
            'piste:type': 'sleigh'
        },
        'Snowshoe': {
            'highway': 'path',
            'piste:type': 'hike'
        },
        'Snowmobile': {
            'highway': 'track',
            'snowmobile': 'yes'
        },
        'Motorized Watercraft': {
            'motorboat': 'yes'
        },
        'Non-Motorized Watercraft': {
            'canoe': 'yes'
        }
    }
}

# Special case
# for when trail use is collection of fields with yes/no values
trailusefields = {
    # Trail use value code : Matching boolean field name
    'Hiker/Pedestrian': 'TRLUSE_FOOT',
    'Pack and Saddle': 'TRLUSE_HORSE',
    'Bicycle': 'TRLUSE_BICYCLE',
    'Motorcycle': 'TRLUSE_MOTORCYCLE',
    'All-Terrain Vehicle': 'TRLUSE_ATV',
    'Four-Wheel Drive Vehicle > 50" in Tread Width': 'TRLUSE_4WD',
    'Cross-Country Ski': 'TRLUSE_NORDIC',
    'Downhill Ski': 'TRLUSE_DOWNHILL',
    'Dog Sled': 'TRLUSE_DOGSLED',
    'Snowshoe': 'TRLUSE_SNOWSHOE',
    'Snowmobile': 'TRLUSE_SNOWMOBILE',
    'Motorized Watercraft': 'TRLUSE_MOTORBOAT',
    'Non-Motorized Watercraft': 'TRLUSE_CANOE'
}
