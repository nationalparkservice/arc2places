import generic


def filterTags(attrs):
    if not attrs:
        return
    tags = generic.filterTags(attrs)

    # defaults
    tags['highway'] = 'road'
    tags['oneway'] = 'no'

    # FIXME renderer uses name for labeling, should we put label in name?
    namemap = {
        'RDNAME': 'name',
        'RDALTNAMES': 'nps:rdaltnames',
        'RDLABEL': 'nps:rdlabel',
        'RDSTATUS': 'nps:rdstatus',
        'RDCLASS': 'nps:rdclass',
        'LANES': 'lanes',
        'ROUTEID': 'nps:routeid',
        'RTENUMBER': 'nps:rtenumber'}

    status = {
        'Existing': ('yes', None),  # access,highway
        'Decommissioned': ('no', None),
        'Temporarily Closed': ('no', None),
        'Proposed': ('no', 'proposed'),  # conflict with class
        'Planned': ('no', 'proposed'),  # conflict with class
        'Unknown': ('no', None)}

    # FIXME: which governs highway tag from class or status?
    # I think it should be status, so it goes second

    rclass = {
        'Unknown': 'road',  # highway
        'Primary': 'primary',
        # 'Primary'  :'primary_link',
        'Secondary': 'secondary',
        # 'Secondary':'secondary_link',
        # 'Local'    :'tertiary',
        # 'Local'    :'tertiary_link',
        'Local': 'residential',
        # 'Local'    :'trunk',
        # 'Local'    :'trunk_link',
        # 'Local'    :'unclassified',
        '4WD': 'road',  # 4wd_only=yes
        'Service': 'service',
        'Private': 'road'}  # access=private

    surface = {
        'Asphalt': 'asphalt',
        'Concrete': 'concrete',
        'Brick/Pavers': 'paving_stones',
        'Cobblestone': 'cobblestone',
        'Gravel': 'gravel',
        'Sand': 'sand',
        'Native or Dirt': 'ground',
        'Unpaved Other': 'unpaved',
        'Paved Other': 'paved',
        'Unknown': None}

    oneway = {
        'With Digitized': 'yes',
        'Against Digitized': '-1'}
    # 'NULL' :'no'}

    for gisname in namemap:
        if gisname in attrs:
            value = attrs[gisname].strip()
            if value:
                tags[namemap[gisname]] = value

    if 'RDCLASS' in attrs and attrs['RDCLASS']:
        class_value = attrs['RDCLASS'].strip()
        for gisclass in rclass:
            if gisclass == class_value:
                osmclass = rclass[gisclass]
                if osmclass:
                    tags['highway'] = osmclass
        if class_value == '4WD':
            tags['4wd_only'] = 'yes'
        if class_value == 'Private':
            tags['access'] = 'private'

    if 'RDSURFACE' in attrs and attrs['RDSURFACE']:
        surface_value = attrs['RDSURFACE'].strip()
        for gissurface in surface:
            if gissurface == surface_value:
                osmsurface = surface[gissurface]
                if osmsurface:
                    tags['surface'] = osmsurface

    if 'ONEWAY' in attrs and attrs['ONEWAY']:
        oneway_value = attrs['ONEWAY'].strip()
        for gisoneway in oneway:
            if gisoneway == oneway_value:
                osmoneway = oneway[gisoneway]
                if osmoneway:
                    tags['oneway'] = osmoneway

    if 'RDSTATUS' in attrs and attrs['RDSTATUS']:
        status_value = attrs['RDSTATUS'].strip()
        for gisstatus in status:
            if gisstatus == status_value:
                osmstatus = status[gisstatus]
                if osmstatus[0]:
                    tags['access'] = osmstatus[0]
                if osmstatus[1]:
                    tags['highway'] = osmstatus[1]

    return tags
