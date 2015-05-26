import generic
import tools
from config_trails import *


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

    # trail use (draft standard)
    # trail use is a '|' separated list of values (this requires a slightly
    # modified version of generic.maptags
    usefieldname = 'TRLUSES'
    trailusemap = valuemap[usefieldname]
    value = tools.valueof(usefieldname, altnames, attrs)
    if value:
        for trailusecode in trailusemap:
            if trailusecode in value:
                tags.update(trailusemap[trailusecode])

    # trail use (proposed breakout)
    # trail use is collection of fields with yes/no values
    for trailusecode, fieldname in trailusefields.items():
        flag = tools.valueof(fieldname, altnames, attrs)
        if flag == 'True' or flag == 'Yes':
            tags.update(trailusemap[trailusecode])

    return tags
