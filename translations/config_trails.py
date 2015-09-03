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
# FIXME: coordinate with aliases in data standard
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
        'nht': {
            'informal': 'no'
        },
        'nst': {
            'informal': 'no'
        },
        'park trail': {
            'informal': 'no'
        },
        'route path': {
            'informal': 'yes'
        },
        'unmaintained trail': {
            'informal': 'yes'
        },
        'unofficial trail': {
            'informal': 'yes'
        },
        'sidewalk': {
            'highway': 'footway',
            'footway': 'sidewalk'
        }
    },
    'TRLTYP': {
        'snow trail': {'piste:type': 'yes'},
        'water trail': {'waterway': 'yes'},
        'standard terra trail': {'highway': 'path'}
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
        'existing': {'access': 'yes'},
        'temporarily closed': {'access': 'no'},
        'decommissioned': {'access': 'no'},
        'proposed': {
            'access': 'no',
            # 'highway': 'proposed'  # TODO: conflict with 'highway':'*' see trails.py for resolution
        },
        'planned': {
            'access': 'no',
            # 'highway': 'proposed'  # TODO: conflict with 'highway':'*' see trails.py for resolution
        }
    },
    'TRLUSE': {
        # FIXME: undefined result when multiple conflicting tags are allowed (i.e. hike and atv)
        'hiker/pedestrian': {
            'highway': 'path',
            'foot': 'yes'
        },
        'pack and saddle': {
            'highway': 'path',
            'horse': 'yes'
        },
        'bicycle': {
            'highway': 'path',
            'bicycle': 'yes'
        },
        'motorcycle': {
            'highway': 'track',
            'motorcycle': 'yes'
        },
        'all-terrain vehicle': {
            'highway': 'track',
            'atv': 'yes'
        },
        'four-wheel drive vehicle > 50" in tread width': {
            'highway': 'track',
            '4wd_only': 'yes'
        },
        'backcountry ski': {
            'piste:type': 'skitour',
            'ski': 'yes'
        },
        'cross-country ski': {
            'piste:type': 'nordic',
            'ski': 'yes'
        },
        'downhill ski': {
            'piste:type': 'downhill',
            'ski': 'yes'
        },
        'dog sled': {
            'piste:type': 'sleigh'
        },
        'snowshoe': {
            'piste:type': 'hike'
        },
        'snowmobile': {
            'highway': 'track',
            'snowmobile': 'yes'
        },
        'motorized watercraft': {
            'motorboat': 'yes',
            'waterway': 'yes'
        },
        'non-motorized watercraft': {
            'canoe': 'yes',
            'waterway': 'yes'
        },
        'human use (social)': {
            'highway': 'path',
            'foot': 'yes',
            'informal': 'yes'
        },
        'non-human use (animal)': {
            'highway': 'path',
            'informal': 'yes'
        },
    }
}

# Special case
# for when trail use is collection of fields with yes/no values
trailusefields = {
    # Trail use value code : Matching boolean field name
    'hiker/pedestrian': 'TRLUSE_FOOT',
    'pack and saddle': 'TRLUSE_HORSE',
    'bicycle': 'TRLUSE_BICYCLE',
    'motorcycle': 'TRLUSE_MOTORCYCLE',
    'all-terrain vehicle': 'TRLUSE_ATV',
    'four-wheel drive vehicle > 50" in tread width': 'TRLUSE_4WD',
    'cross-country ski': 'TRLUSE_NORDIC',
    'downhill ski': 'TRLUSE_DOWNHILL',
    'dog sled': 'TRLUSE_DOGSLED',
    'snowshoe': 'TRLUSE_SNOWSHOE',
    'snowmobile': 'TRLUSE_SNOWMOBILE',
    'motorized watercraft': 'TRLUSE_MOTORBOAT',
    'non-motorized watercraft': 'TRLUSE_CANOE'
    # FIXME: TRLUSE_CANYONEERING, etc
}
