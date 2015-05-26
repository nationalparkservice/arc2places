import generic
import tools
from config_buildings import *


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

    return tags
