import generic


# noinspection PyPep8Naming
def filterTags(attrs):
    if not attrs:
        return

    namemap = {
        'RDNAME': 'name',
        'RDALTNAMES': 'nps:road_alt_names',
        'RDLABEL': 'nps:road_label',
        'RDSTATUS': 'nps:road_status',
        'RDCLASS': 'nps:road_class',
        'RDMAINTAINER': 'nps:road_maintainer',
        'LANES': 'lanes',
        'ROUTEID': 'nps:route_id',
        'RTENUMBER': 'nps:route_number'
    }

    altnames = {
        'RDNAME': ['NAME', 'ROADNAME', 'RD_NAME', 'ROAD_NAME'],
        'RDALTNAMES': ['ALTNAMES', 'ROADALTNAMES', 'RD_ALTNAMES',
                       'ROAD_ALTNAMES'],
        'RDLABEL': ['LABEL', 'ROADLABEL', 'RD_LABEL', 'ROAD_LABEL'],
        'RDSTATUS': ['STATUS', 'ROADSTATUS', 'RD_STATUS', 'ROAD_STATUS'],
        'RDCLASS': ['CLASS', 'ROADCLASS', 'RD_CLASS', 'ROAD_CLASS'],
        'RDMAINTAINER': ['MAINTAINER', 'ROADMAINTAINER', 'RD_MAINTAINER',
                         'ROAD_MAINTAINER'],
        'ROUTEID': ['ROUTE', 'ROUTE_ID'],
        'RTENUMBER': ['RTE_NUMBER', 'ROUTENUMBER', 'ROUTE_NUMBER']
    }

    # must do class before status because of overlap with proposed status
    multimaps = {
        'RDCLASS': (
            ['highway', 'access', '4wd_only'],
            {
                'Primary': ('primary', None, None),
                'Secondary': ('secondary', None, None),
                'Local': ('residential', None, None),
                '4WD': ('road', None, 'yes'),
                'Service': ('service', 'private', None),
                'Private': ('road', None, None)
            }
        ),
        'RDSTATUS': (
            ['access', 'highway'],
            {
                'Existing': ('yes', None),
                'Decommissioned': ('no', None),
                'Temporarily Closed': ('no', None),
                'Proposed': ('no', 'proposed'),  # overlap with class
                'Planned': ('no', 'proposed')  # overlap with class
            }
        ),
        'RDSURFACE': (
            ['surface'],
            {
                'Asphalt': 'asphalt',
                'Concrete': 'concrete',
                'Brick/Pavers': 'paving_stones',
                'Cobblestone': 'cobblestone',
                'Gravel': 'gravel',
                'Sand': 'sand',
                'Native or Dirt': 'ground',
                'Unpaved Other': 'unpaved',
                'Paved Other': 'paved'
            }
        ),
        'ONEWAY': (
            ['oneway'],
            {
                'With Digitized': 'yes',
                'Against Digitized': '-1'
            }
        )
    }

    # generics tags
    tags = generic.filterTags(attrs)

    # default tags
    tags['highway'] = 'road'
    tags['oneway'] = 'no'
    tags['access'] = 'no'

    # simple tags
    tags.update(generic.simplemap(namemap, altnames, attrs))

    # multi tags
    for name in multimaps:
        tagz, valuesmap = multimaps[name]
        tags.update(generic.fancymap(name, altnames, attrs, tagz, valuesmap))

    # special case when status is proposed/planned, then put class in proposed
    if tags['highway'] == 'proposed':
        name = 'RDCLASS'
        tagz, valuesmap = multimaps[name]
        tagz = ['proposed']
        generic.fancymap(name, altnames, attrs, tagz, valuesmap)

    return tags
