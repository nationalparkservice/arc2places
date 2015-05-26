import tools
from config_generic import *


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
