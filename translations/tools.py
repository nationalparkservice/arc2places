def valueof(name, altnames, attributes, no_values=('null', 'none', 'unknown')):
    value = None
    if name in attributes:
        value = attributes[name]
    else:
        if name in altnames:
            for altname in altnames[name]:
                if altname in attributes:
                    value = attributes[altname]
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
        for tagkey in tagmap:
            if tagkey == value:
                tags.update(tagmap[tagkey])
    return tags
