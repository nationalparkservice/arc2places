import generic


def filterTags(attrs):
    if not attrs:
        return

    namemap = {
        'TRLNAME': 'name',
        'TRLALTNAMES': 'nps:trlaltnames',
        'TRLFEATTYPE': 'nps:trlfeattype',
        'TRLSTATUS': 'nps:trlstatus',
        'TRLTYPE': 'nps:trltype',
        'TRLCLASS': 'tracktype',
        'TRLUSES': 'nps:trluses',
    }

    altnames = {
        'TRLNAME': ['NAME', 'TRAILNAME', 'TRL_NAME', 'TRAIL_NAME'],
        'TRLALTNAMES': ['ALTNAMES', 'TRAILALTNAMES', 'TRL_ALTNAMES', 'TRAIL_ALTNAMES'],
        'TRLFEATTYPE': ['FEATTYPE', 'TRAILFEATTYPE', 'TRL_FEATTYPE', 'TRAIL_FEATTYPE'],
        'TRLSTATUS': ['STATUS', 'TRAILSTATUS', 'TRL_STATUS', 'TRAIL_STATUS'],
        'TRLTYPE': ['TYPE', 'TRAILTYPE', 'TRL_TYPE', 'TRAIL_TYPE'],
        'TRLCLASS': ['CLASS', 'TRAILCLASS', 'TRL_CLASS', 'TRAIL_CLASS'],
        'TRLUSES': ['USES', 'TRAILUSES', 'TRL_USES', 'TRAIL_USES']
    }

    multimaps = {
        'TRLCLASS': (
            ['tracktype'],
            {
                'Trail Class 1: Minimally Developed': 'grade5',
                'Trail Class 2: Moderately Developed': 'grade4',
                'Trail Class 3: Developed': 'grade3',
                'Trail Class 4: Highly Developed': 'grade2',
                'Trail Class 5: Fully Developed': 'grade1'
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
        )
    }

    # generics tags
    tags = generic.filterTags(attrs)

    # default tags
    tags['highway'] = 'path'
    tags['horse'] = 'no'
    tags['bicycle'] = 'no'
    tags['motorcycle'] = 'no'
    tags['atv'] = 'no'
    tags['snowmobile'] = 'no'

    # simple tags
    tags.update(generic.simplemap(namemap, altnames, attrs))

    # multi tags
    for name in multimaps:
        tagz, valuesmap = multimaps[name]
        tags.update(generic.fancymap(name, altnames, attrs, tagz, valuesmap))

    a = {
        'Hiker/Pedestrian': {
            'highway': 'path',
            'foot': 'yes'
        },
        'Pack and Saddle': {
            'highway': 'track',
            'horse': 'yes'
        },
        'Bicycle': {
            'highway': 'track',
            'bicycle': 'yes'
        },
        'Motorcycle': {
            'highway': 'track',
            'motorcycle': 'yes'
        },
        'All-Terrain Vehicle': {
            'highway': 'track',
            'atv': 'yes'
        },
        'Four-Wheel Drive Vehicle > 50" in Tread Width': {
            'highway': 'track',
            '4wd_only': 'yes'
        },
        'Cross-Country Ski': {
            'highway': 'path',
            'piste:type': 'nordic'
        },
        'Downhill Ski': {
            'highway': 'path',
            'piste:type': 'downhill'
        },
        'Dog Sled': {
            'highway': 'track',
            'piste:type': 'sleigh'
        },
        'Snowshoe': {
            'highway': 'path',
            'piste:type': 'hike'
        },
        'Snowmobile': {
            'highway': 'track',
            'snowmobile': 'yes'
        },
        'Motorized Watercraft': {
            'motorboat': 'yes'
        },
        'Non-Motorized Watercraft': {
            'canoe': 'yes'
        }
    }

    v = generic.valueof('TRLUSES', altnames, attrs)
    if v:
        for name in a:
            if name in v:
                tags.update(a[name])


if 'TRLUSE_FOOT' in attrs and attrs['TRLUSE_FOOT'] == 'Yes':
    tags['highway'] = 'path'
    tags['foot'] = 'yes'
if 'TRLUSE_HORSE' in attrs and attrs['TRLUSE_HORSE'] == 'Yes':
    tags['highway'] = 'track'
    tags['horse'] = 'yes'
if 'TRLUSE_BICYCLE' in attrs and attrs['TRLUSE_BICYCLE'] == 'Yes':
    tags['highway'] = 'track'
    tags['bicycle'] = 'yes'
if 'TRLUSE_MOTORCYCLE' in attrs and attrs['TRLUSE_MOTORCYCLE'] == 'Yes':
    tags['highway'] = 'track'
    tags['motorcycle'] = 'yes'
if 'TRLUSE_ATV' in attrs and attrs['TRLUSE_ATV'] == 'Yes':
    tags['highway'] = 'track'
    tags['atv'] = 'yes'
if 'TRLUSE_4WD' in attrs and attrs['TRLUSE_4WD'] == 'Yes':
    tags['highway'] = 'track'
    tags['4wd_only'] = 'yes'
if 'TRLUSE_NORDIC' in attrs and attrs['TRLUSE_NORDIC'] == 'Yes':
    tags['highway'] = 'path'
    tags['piste:type'] = 'nordic'
if 'TRLUSE_DOWNHILL' in attrs and attrs['TRLUSE_DOWNHILL'] == 'Yes':
    tags['highway'] = 'path'
    tags['piste:type'] = 'downhill'
if 'TRLUSE_DOGSLED' in attrs and attrs['TRLUSE_DOGSLED'] == 'Yes':
    tags['highway'] = 'track'
    tags['piste:type'] = 'sleigh'
if 'TRLUSE_SNOWSHOE' in attrs and attrs['TRLUSE_SNOWSHOE'] == 'Yes':
    tags['highway'] = 'path'
    tags['piste:type'] = 'hike'
if 'TRLUSE_SNOWMOBILE' in attrs and attrs['TRLUSE_SNOWMOBILE'] == 'Yes':
    tags['highway'] = 'track'
    tags['snowmobile'] = 'yes'
if 'TRLUSE_MOTORBOAT' in attrs and attrs['TRLUSE_MOTORBOAT'] == 'Yes':
    tags['motorboat'] = 'yes'
if 'TRLUSE_CANOE' in attrs and attrs['TRLUSE_CANOE'] == 'Yes':
    tags['canoe'] = 'yes'

if 'TRLFEATTYPE' in attrs and attrs['TRLFEATTYPE']:
    if 'Sidewalk Centerline' == attrs['TRLFEATTYPE']:
        tags['highway'] = 'footway'
        tags['footway'] = 'sidewalk'

return tags
