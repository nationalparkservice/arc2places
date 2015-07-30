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

    # trail use (draft standard)
    # trail use is a '|' separated list of values (this requires a slightly
    # modified version of generic.maptags
    usefieldname = 'TRLUSE'
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
