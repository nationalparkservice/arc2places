import generic
import tools
from config_roads import *


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

    # NOTE: Planned/Proposed roads lose their class.
    # dictionaries are unsorted, so class may not be applied before
    # status. This will fix that per OSM standards
    # http://wiki.openstreetmap.org/wiki/Tag:highway%3Dproposed
    road_status = tools.valueof('RDSTATUS', altnames, attrs)
    if road_status == 'Planned' or road_status == 'Proposed':
        road_class = tools.valueof('RDCLASS', altnames, attrs)
        if road_class:
            tags.update({
                'highway': 'proposed',
                'proposed': road_class
            })

    return tags
