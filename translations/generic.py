def filterTags(attrs):
    if not attrs:
        return
    tags = {}

    namemap = {
        # 'EGIS COLUMN NAME' : 'osm/places tag name'
        # with ogr2osm, the column names are case sensitive
        # with arc2osm, all column names are converted to upper case
        # all osm/places tags should be lower case
        # 'PLACESID'   :Ignore
        'UNITCODE': 'nps:unit_code',
        'UNITNAME': 'nps:unitname',
        'GROUPCODE': 'nps:groupcode',
        'REGIONCODE': 'nps:regioncode',
        'LOCATIONID': 'nps:locationid',
        'ASSETID': 'nps:assetid',
        'ISEXTANT': 'nps:isextant',
        'MAPMETHOD': 'nps:mapmethod',
        'MAPSOURCE': 'source',
        'SOURCESCALE': 'nps:sourcescale',
        'SOURCEDATE': 'nps:sourcedate',
        'XYERROR': 'nps:xyerror',
        'NOTES': 'note',
        'RESTRICTION': 'nps:restriction',
        'DISTRIBUTE': 'nps:distribute',
        'CREATEDATE': 'nps:createdate',
        'CREATEUSER': 'nps:createuser',
        'EDITDATE': 'nps:editdate',
        'EDITUSER': 'nps:edituser',
        'FEATUREID': 'nps:featureid',
        'GEOMETRYID': 'nps:source_id'
    }

    for gisname in namemap:
        if gisname in attrs:
            value = attrs[gisname]
            if value and value != 'Unknown':
                tags[namemap[gisname]] = value

    return tags
