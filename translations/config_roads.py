defaults = {
    u'highway': u'road'
}

fieldmap = {
    u'maintainer': u'nps:road_maintainer',
    u'rdaltname': u'alt_name',
    u'rdclass': u'nps:road_class',
    u'rdlabel': u'name',
    u'rdlanes': u'lanes',
    u'rdname': u'official_name',
    u'rdoneway': u'oneway',
    u'rdstatus': u'nps:road_status',
    u'rdsurface': u'surface',
    u'routeid': u'nps:route_id',
    u'rtenumber': u'nps:route_number'
}

altnames = {
    u'maintainer': [u'rdmaintainer', u'roadmaintainer', u'rd_maintainer', u'road_maintainer', u'primaryroadmaintainer', u'primary_road_maintainer'],
    u'rdaltname': [u'altname', u'alt_name', u'alternatename', u'altername_name', u'rd_altname', u'rd_alt_name', u'rdalternatename', u'rd_alternamename', u'rd_altername_name', u'roadaltname', u'road_altname', u'road_alt_name', u'roadalternatename', u'road_alternamename', u'road_altername_name', u'altnames', u'alt_names', u'alternatenames', u'altername_names', u'rdaltnames', u'rd_altnames', u'rd_alt_names', u'rdalternatenames', u'rd_alternamenames', u'rd_altername_names', u'roadaltnames', u'road_altnames', u'road_alt_names', u'roadalternatenames', u'road_alternamenames', u'road_altername_names'],
    u'rdclass': [u'class', u'roadclass', u'rd_class', u'road_class', u'administrative_road_class'],
    u'rdlabel': [u'label', u'roadlabel', u'rd_label', u'road_label', u'rdname', u'name', u'roadname', u'rd_name', u'road_name'],
    u'rdlanes': [u'lanes', u'roadlanes', u'rd_lanes', u'road_lanes', u'numberoflanes', u'number_of_lanes'],
    u'rdname': [u'name', u'roadname', u'rd_name', u'road_name'],
    u'rdoneway': [u'oneway', u'one_way', u'roadoneway', u'rd_oneway', u'road_oneway', u'road_one_way'],
    u'rdstatus': [u'status', u'roadstatus', u'rd_status', u'road_status'],
    u'rdsurface': [u'surface', u'roadsurface', u'rd_surface', u'road_surface'],
    u'routeid': [u'route', u'route_id', u'fhwa_nps_route_id'],
    u'rtenumber': [u'rte_number', u'routenumber', u'route_number']
}

valuemap = {
    u'isbridge': {
        u'true': {u'bridge': u'yes'},
        u'y': {u'bridge': u'yes'},
        u'yes': {u'bridge': u'yes'}
    },
    u'istunnel': {
        u'true': {u'tunnel': u'yes'},
        u'y': {u'tunnel': u'yes'},
        u'yes': {u'tunnel': u'yes'}
    },
    u'rdclass': {
        u'4 wheeler': {u'4wd_only': u'yes', u'highway': u'road'},
        u'4-wheeler': {u'4wd_only': u'yes', u'highway': u'road'},
        u'4wd': {u'4wd_only': u'yes', u'highway': u'road'},
        u'access road': {u'highway': u'service'},
        u'county highway': {u'highway': u'secondary'},
        u'four wheeler': {u'4wd_only': u'yes', u'highway': u'road'},
        u'four-wheel drive road': {u'4wd_only': u'yes', u'highway': u'road'},
        u'four-wheeler': {u'4wd_only': u'yes', u'highway': u'road'},
        u'freeway': {u'highway': u'motorway'},
        u'freeway ramp': {u'highway': u'motorway_link'},
        u'highway': {u'highway': u'motorway'},
        u'highway link': {u'highway': u'motorway_link'},
        u'highway ramp': {u'highway': u'motorway_link'},
        u'interstate': {u'highway': u'motorway'},
        u'interstate highway': {u'highway': u'motorway'},
        u'local': {u'highway': u'residential'},
        u'minor road': {u'highway': u'unclassified'},
        u'motorway': {u'highway': u'motorway'},
        u'parking aisle': {u'service': u'parking_aisle', u'highway': u'service'},
        u'pedestrian road': {u'highway': u'pedestrian'},
        u'pedestrian street': {u'highway': u'pedestrian'},
        u'primary': {u'highway': u'primary'},
        u'primary link': {u'highway': u'primary_link'},
        u'primary ramp': {u'highway': u'primary_link'},
        u'primary road': {u'highway': u'primary'},
        u'private': {u'access': u'private', u'highway': u'road'},
        u'private road': {u'access': u'private', u'highway': u'road'},
        u'residential': {u'highway': u'residential'},
        u'residential road': {u'highway': u'residential'},
        u'road': {u'highway': u'yes'},
        u'secondary': {u'highway': u'secondary'},
        u'secondary link': {u'highway': u'secondary_link'},
        u'secondary ramp': {u'highway': u'secondary_link'},
        u'secondary road': {u'highway': u'secondary'},
        u'service': {u'highway': u'service'},
        u'service road': {u'highway': u'service'},
        u'state highway': {u'highway': u'primary'},
        u'state route': {u'highway': u'primary'},
        u'tertiary': {u'highway': u'tertiary'},
        u'tertiary link': {u'highway': u'tertiary_link'},
        u'tertiary ramp': {u'highway': u'tertiary_link'},
        u'tertiary road': {u'highway': u'tertiary'},
        u'turnpike': {u'highway': u'motorway'},
        u'unclassified': {u'highway': u'unclassified'},
        u'unclassified road': {u'highway': u'unclassified'},
        u'unknown road': {u'highway': u'road'},
        u'us highway': {u'highway': u'primary'}
    },
    u'rdoneway': {
        u'against digitized': {u'oneway': u'-1'},
        u'backwards': {u'oneway': u'-1'},
        u'forward': {u'oneway': u'yes'},
        u'with digitized': {u'oneway': u'yes'},
        u'yes': {u'oneway': u'yes'}
    },
    u'rdstatus': {
        u'closed': {u'access': u'no'},
        u'decommissioned': {u'access': u'no'},
        u'planned': {u'access': u'no'},
        u'proposed': {u'access': u'no'},
        u'temporarily closed': {u'access': u'no'}
    },
    u'rdsurface': {
        u'asphalt': {u'surface': u'asphalt'},
        u'brick': {u'surface': u'paving_stones'},
        u'brick/pavers': {u'surface': u'paving_stones'},
        u'bricks': {u'surface': u'paving_stones'},
        u'cobbles': {u'surface': u'cobblestone'},
        u'cobblestone': {u'surface': u'cobblestone'},
        u'cobblestones': {u'surface': u'cobblestone'},
        u'concrete': {u'surface': u'concrete'},
        u'dirt': {u'surface': u'ground'},
        u'gravel': {u'surface': u'gravel'},
        u'ground': {u'surface': u'ground'},
        u'native': {u'surface': u'ground'},
        u'native or dirt': {u'surface': u'ground'},
        u'other, paved': {u'surface': u'paved'},
        u'other, unpaved': {u'surface': u'unpaved'},
        u'paved': {u'surface': u'paved'},
        u'paved other': {u'surface': u'paved'},
        u'pavers': {u'surface': u'paving_stones'},
        u'paving stones': {u'surface': u'paving_stones'},
        u'sand': {u'surface': u'sand'},
        u'unpaved': {u'surface': u'unpaved'},
        u'unpaved other': {u'surface': u'unpaved'}
    }
}
