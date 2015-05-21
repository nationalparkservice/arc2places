import generic


def filterTags(attrs):
    if not attrs:
        return
    tags = generic.filterTags(attrs)

    # defaults
    tags['highway'] = 'path'
    tags['horse'] = 'no'
    tags['bicycle'] = 'no'
    tags['motorcycle'] = 'no'
    tags['atv'] = 'no'
    tags['snowmobile'] = 'no'

    namemap = {
        'TRLNAME': 'name',
        'TRLALTNAMES': 'nps:trlaltnames',
        'TRLFEATTYPE': 'nps:trlfeattype',
        'TRLSTATUS': 'nps:trlstatus',
        'TRLTYPE': 'nps:trltype',
        'TRLCLASS': 'tracktype',
        'TRLUSES': 'nps:trluses',
        # draft standard
        'TRAILNAME': 'name',
        'ALTNAMES': 'nps:trlaltnames',
        'FEATTYPE': 'nps:trlfeattype',
        'TRAILTYPE': 'nps:trltype',
        'TRAILCLASS': 'tracktype',
        'TRAILSTATUS': 'nps:trlstatus',
        'TRAILUSES': 'nps:trluses'
        # 'VISACCESS'  :
    }

    for gisname in namemap:
        if gisname in attrs:
            value = attrs[gisname].strip()
            if value:
                tags[namemap[gisname]] = value

    trlclass = {
        'Unknown': None,
        'Trail Class 1: Minimally Developed': 'grade5',
        'Trail Class 2: Moderately Developed': 'grade4',
        'Trail Class 3: Developed': 'grade3',
        'Trail Class 4: Highly Developed': 'grade2',
        'Trail Class 5: Fully Developed': 'grade1'
    }

    if 'TRLCLASS' in attrs and attrs['TRLCLASS']:
        class_value = attrs['TRLCLASS'].strip()
        for gis_class in trlclass:
            if gis_class == class_value:
                osm_class = trlclass[gis_class]
                if osm_class:
                    tags['tracktype'] = osm_class

    # TRLUSES is a pipe (|) separated list of uses    
    if 'TRLUSES' in attrs and attrs['TRLUSES']:
        if 'Hiker/Pedestrian' in attrs['TRLUSES']:
            tags['highway'] = 'path'
            tags['foot'] = 'yes'
        if 'Pack and Saddle' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['horse'] = 'yes'
        if 'Bicycle' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['bicycle'] = 'yes'
        if 'Motorcycle' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['motorcycle'] = 'yes'
        if 'All-Terrain Vehicle' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['atv'] = 'yes'
        if 'Four-Wheel Drive Vehicle > 50" in Tread Width' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['4wd_only'] = 'yes'
        if 'Cross-Country Ski' in attrs['TRLUSES']:
            tags['highway'] = 'path'
            tags['piste:type'] = 'nordic'
        if 'Downhill Ski' in attrs['TRLUSES']:
            tags['highway'] = 'path'
            tags['piste:type'] = 'downhill'
        if 'Dog Sled' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['piste:type'] = 'sleigh'
        if 'Snowshoe' in attrs['TRLUSES']:
            tags['highway'] = 'path'
            tags['piste:type'] = 'hike'
        if 'Snowmobile' in attrs['TRLUSES']:
            tags['highway'] = 'track'
            tags['snowmobile'] = 'yes'
        if 'Motorized Watercraft' in attrs['TRLUSES']:
            tags['motorboat'] = 'yes'
        if 'Non-Motorized Watercraft' in attrs['TRLUSES']:
            tags['canoe'] = 'yes'

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
