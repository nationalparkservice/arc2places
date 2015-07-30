import tools
from config_generic import *


# noinspection PyPep8Naming,PyUnusedLocal
def filterFeature(feature, fieldnames, reproject):
    # Places override
    inplaces = tools.feature_value('INPLACES', altnames, feature, fieldnames)
    if inplaces is not None:
        if inplaces == 'Yes':
            return feature
        else:
            return None
    else:
        restriction = tools.feature_value('RESTRICT', altnames,
                                          feature, fieldnames)
        is_unrestricted = restriction is None or restriction == 'Unrestricted'
        distribute = tools.feature_value('DISTRIBUTE', altnames,
                                         feature, fieldnames)
        is_distributable = distribute is None or distribute == 'Public'
        if is_unrestricted and is_distributable:
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
