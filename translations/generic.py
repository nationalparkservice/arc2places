import tools
from config_generic import *


# noinspection PyPep8Naming,PyUnusedLocal
def filterFeature(feature, fieldnames, reproject):
    restriction = tools.feature_value('RESTRICT', altnames,
                                      feature, fieldnames)
    distribute = tools.feature_value('DISTRIBUTE', altnames,
                                     feature, fieldnames)
    if (distribute is None or distribute == 'Public') and \
       (restriction is None or restriction == 'Unrestricted'):
        return feature
    else:
        return None


# noinspection PyPep8Naming
def filterTags(attrs):
    if not attrs:
        return

    tags = {}

    # default tags
    tags.update(defaults)

    # simple tags
    tags.update(tools.simplemap(fieldmap, altnames, attrs))

    # multi tags
    for fieldname in valuemap:
        tagmap = valuemap[fieldname]
        tags.update(tools.maptags(fieldname, altnames, attrs, tagmap))

    return tags
