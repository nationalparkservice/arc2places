# Based on the Places Data Schema revision 6 (5/18/2015)
# https://github.com/nationalparkservice/places-data/wiki/Places-Data-Schema-Guide
# with ogr2osm, the GIS field names are case sensitive
# with arc2osm, all GIS field names are converted to upper case
# all osm/Places tags should be lower case

# All config files must have defaults, fieldmap, altnames and valuemap

# default tags for trail *lines* in Places
defaults = {
    # 'highway': 'path',  # not appropriate for 'piste:type' and 'waterway'; set in trails.py if needed.
    # 'access': 'no',  # unknown unless explicitly set with value from TRLSTATUS
    # FIXME: decide if default is unknown or denied (currently denied
    'foot': 'no',
    'horse': 'no',
    'bicycle': 'no',
    'motor_vehicles': 'no',
    'ski': 'no'
    # 'wheelchair': 'no',  # eGIS standard is slient on this; defer to any value set in Places
}

# values map one to one from field name to OSM tag
fieldmap = {
    # GIS_FieldName : Places Tag
    'TRLNAME': 'nps:trail_name',
    'TRLALTNAME': 'nps:trail_alt_name',
    'TRLLABEL': 'name',
    'TRLFEATTYPE': 'nps:trail_feat_type',
    'TRLSTATUS': 'nps:trail_status',
    'TRLTYPE': 'nps:trail_type',
    'TRLTRACK': 'nps:trail_track',
    'TRLCLASS': 'tracktype',
    'TRLUSE': 'nps:trail_uses',
    'TRLISADMIN': 'nps:trail_is_admin',
    'TRLDESC': 'nps:trail_description',
    'WHLENGTH': 'nps:trail_wheel_length',
    'WHLENUOM': 'nps:trail_wheel_length_UOM',
    # Non-standard (pre-standard) attributes
    'TRLSURFACE': 'surface'
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
    'TRLTRACK': ['TRACK', 'TRAILTRACK', 'TRL_TRACK', 'TRAIL_TRACK'],
    'TRLCLASS': ['CLASS', 'TRAILCLASS', 'TRL_CLASS', 'TRAIL_CLASS'],
    'TRLUSE': ['USE', 'TRAILUSE', 'TRL_USE', 'TRAIL_USE', 'USES', 'TRAILUSES',
               'TRLUSES', 'TRL_USES', 'TRAIL_USES'],
    'TRLISADMIN': ['ISADMIN', 'TRAILISADMIN', 'TRL_ISADMIN', 'TRAIL_ISADMIN', 'ADMIN', 'ADMINISTRATIVE'],
    'TRLDESC': ['TRL_DESC', 'TRAIL_DESC', 'TRAILDESC', 'DESCRIPTION', 'TRAIL_DESCRIPTION'],
    'WHLENGTH': ['WH_LENGTH', 'WHEEL_LENGTH'],
    'WHLENUOM': ['WH_LEN_UOM', 'WH_LENGTH_UOM', 'WHEEL_LENGTH_UOM']
}

# GIS field names where different values map to a specific set of Places tags
valuemap = {
    # GIS_FieldName : {GIS_Value: {tag:value, ... }, ...}
    'TRLFEATTYPE': {
        'NHT': {
            'informal': 'no'
        },
        'NST': {
            'informal': 'no'
        },
        'Park Trail': {
            'informal': 'no'
        },
        'Route Path': {
            'informal': 'yes'
        },
        'Unmaintained Trail': {
            'informal': 'yes'
        },
        'Unofficial Trail': {
            'informal': 'yes'
        },
        'Sidewalk': {
            'highway': 'footway',
            'footway': 'sidewalk'
        }
    },
    'TRLTYP': {
        'Snow Trail': {'piste:type': 'yes'},
        'Water Trail': {'waterway': 'yes'},
        'Standard Terra Trail': {'highway': 'path'}
    },
    'TRLCLASS': {
        # '*': {'tracktype': '*'}  # by fieldmap
        '2110': {'tracktype': 'grade5'},
        '2120': {'tracktype': 'grade4'},
        '2130': {'tracktype': 'grade3'},
        '2140': {'tracktype': 'grade2'},
        '2150': {'tracktype': 'grade1'}
    },
    'TRLSTATUS': {
        'Existing': {'access': 'yes'},
        'Temporarily Closed': {'access': 'no'},
        'Decommissioned': {'access': 'no'},
        'Proposed': {
            'access': 'no',
            # 'highway': 'proposed'  # TODO: conflict with 'highway':'*' see trails.py for resolution
        },
        'Planned': {
            'access': 'no',
            # 'highway': 'proposed'  # TODO: conflict with 'highway':'*' see trails.py for resolution
        }
    },
    'TRLUSE': {
        # FIXME: undefined result when multiple conflicting tags are allowed (i.e. hike and atv)
        'Hiker/Pedestrian': {
            'highway': 'path',
            'foot': 'yes'
        },
        'Pack and Saddle': {
            'highway': 'path',
            'horse': 'yes'
        },
        'Bicycle': {
            'highway': 'path',
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
        'Backcountry Ski': {
            'piste:type': 'skitour',
            'ski': 'yes'
        },
        'Cross-Country Ski': {
            'piste:type': 'nordic',
            'ski': 'yes'
        },
        'Downhill Ski': {
            'piste:type': 'downhill',
            'ski': 'yes'
        },
        'Dog Sled': {
            'piste:type': 'sleigh'
        },
        'Snowshoe': {
            'piste:type': 'hike'
        },
        'Snowmobile': {
            'highway': 'track',
            'snowmobile': 'yes'
        },
        'Motorized Watercraft': {
            'motorboat': 'yes',
            'waterway': 'yes'
        },
        'Non-Motorized Watercraft': {
            'canoe': 'yes',
            'waterway': 'yes'
        },
        'Human Use (Social)': {
            'highway': 'path',
            'foot': 'yes',
            'informal': 'yes'
        },
        'Non-Human Use (Animal)': {
            'highway': 'path',
            'informal': 'yes'
        },
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
