import generic
import tools
from config_trails import *


def fields_for_tag(tag_name):
    fields = tools.fields_for_tag(tag_name, fieldmap, altnames)
    if fields is None:
        fields = generic.fields_for_tag(tag_name)
    return fields


# noinspection PyPep8Naming
def filterFeature(feature, fieldnames, reproject):
    return generic.filterFeature(feature, fieldnames, reproject)


# noinspection PyPep8Naming
def filterTags(attrs):
    if not attrs:
        return

    # generics tags
    tags = generic.filterTags(attrs)

    # default tags
    tags.update(defaults)

    # simple tags
    tags.update(tools.simplemap(fieldmap, altnames, attrs))

    # multi tags
    for fieldname in valuemap:
        tagmap = valuemap[fieldname]
        tags.update(tools.maptags(fieldname, altnames, attrs, tagmap))

    # Special Instructions

    # trail use is a pipe (|) delimiter separated list of values
    # these are permitted activities; Permission of other activities is unknown.
    # (this requires a slightly modified version of generic.maptags)
    # Split on '|' first.  we do not want 'motorized' to match '...|non-motorized|...'
    usefieldname = 'TRLUSE'
    trailusemap = valuemap[usefieldname]
    value = tools.valueof(usefieldname, altnames, attrs)
    if value:
        value_lower = value.lower()
        values = value_lower.split('|')
        for trailusecode in trailusemap:
            if trailusecode in values:
                tags.update(trailusemap[trailusecode])

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
        'backcountry ski': 'TRLUSE_SKITOUR',
        'cross-country ski': 'TRLUSE_NORDIC',
        'downhill ski': 'TRLUSE_DOWNHILL',
        'dog sled': 'TRLUSE_DOGSLED',
        'snowshoe': 'TRLUSE_SNOWSHOE',
        'snowmobile': 'TRLUSE_SNOWMOBILE',
        'motorized watercraft': 'TRLUSE_MOTORBOAT',
        'non-motorized watercraft': 'TRLUSE_CANOE',
        'canyoneering route': 'TRLUSE_CANYONEER',
        'climbing route': 'TRLUSE_CLIMB'
    }

    # trail use may be a collection of fields with yes/no values
    # A negative value is the same as a missing column or null/unknown value
    for trailusecode, fieldname in trailusefields.items():
        flag = tools.valueof(fieldname, altnames, attrs)
        if flag and (flag.lower() == 'true' or flag.lower() == 'yes' or flag.lower() == 'y'):
            try:
                tags.update(trailusemap[trailusecode])
            except KeyError:
                pass  # protect against boolean fields without a matching set of tags

    # highway is not defined and piste:type is not defined, add highway = path
    if 'highway' not in tags and 'piste:type' not in tags and 'waterway' not in tags:
        tags['highway'] = 'path'

    # Possible conflit on highway between TRLFEATURETYPE or TRLUSE == sidewalk, and other trail types.
    # Winner is sidewalk.
    if 'footway' in tags and tags['footway'] == 'sidewalk':
        tags['highway'] = 'footway'

    # Planned/Proposed trails have their 'highway' value set to 'proposed'.
    # and thier 'proposed' value set to thier 'highway' value
    # similar to the OSM standard for roads
    # http://wiki.openstreetmap.org/wiki/Tag:highway%3Dproposed
    trail_status = tools.valueof('trlstatus', altnames, attrs)
    if trail_status and (trail_status.lower() == 'planned' or trail_status.lower() == 'proposed'):
        if 'highway' in tags:
            tags.update({
                'highway': 'proposed',
                'proposed': tags['highway']
            })
        elif 'piste:type' in tags:
            tags.update({
                'piste:type': 'proposed',
                'proposed': tags['piste:type']
            })
        elif 'waterway' in tags:
            tags.update({
                'waterway': 'proposed',
                'proposed': tags['waterway']
            })
        elif 'footway' in tags:
            tags.update({
                'footway': 'proposed',
                'proposed': tags['footway']
            })
        else:
            tags['proposed'] = 'yes'

    return tags
