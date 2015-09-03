import sys


def valueof(name, altnames, attributes, no_values=('null', 'none', 'unknown')):
    value = None
    if name in attributes:
        value = attributes[name]
    else:
        if name in altnames:
            for altname in altnames[name]:
                if altname in attributes:
                    value = attributes[altname]
                    break  # Use the first, not the last, matching name
    if value:
        value = value.strip()
        if value.lower() in no_values:
            value = None
    return value


def simplemap(namemap, altnames, attributes):
    tags = {}
    for gisname in namemap:
        value = valueof(gisname, altnames, attributes)
        if value:
            tagname = namemap[gisname]
            tags[tagname] = value
    return tags


def maptags(fieldname, altnames, attrs, tagmap):
    tags = {}
    value = valueof(fieldname, altnames, attrs)
    if value:
        value_lower = value.lower()
        for tagkey in tagmap:
            if tagkey == value_lower:
                tags.update(tagmap[tagkey])
    return tags


def feature_value(name, altnames, feature, fieldnames,
                  no_values=('null', 'none', 'unknown')):
    # feature can be an Arcpy feature or an OGR feature
    index = -1
    if name in fieldnames:
        index = fieldnames.index(name)
    else:
        if name in altnames:
            for altname in altnames[name]:
                if altname in fieldnames:
                    index = fieldnames.index(altname)
    value = None
    if 0 <= index:
        try:
            # ogr feature
            value = feature.GetFieldAsString(index)
        except AttributeError:
            # arc feature
            value = feature[index]
        if value:
            if sys.version[0] < '3':
                # unicode command was removed in python 3.x
                value = unicode(value).strip()
            else:
                value = str(value).strip()
            if value.lower() in no_values:
                value = None
        else:
            value = None
    return value


def fields_for_tag(tag_name, namemap, altnames):
    primary_name = None
    for name in namemap:
        if namemap[name] == tag_name:
            primary_name = name
            break
    if primary_name is None:
        return None
    if primary_name in altnames:
        return [primary_name] + altnames[primary_name]
    return [primary_name]
