defaults = {}

fieldmap = {
    u'poialtname': u'alt_name',
    u'poidesc': u'nps:poi_description',
    u'poifeattype': u'nps:poi_feature_type',
    u'poilabel': u'name',
    u'poiname': u'official_name',
    u'poitype': u'nps:poi_type'
}

altnames = {
    u'poialtname': [u'altname', u'alt_name', u'alternatename', u'altername_name', u'poi_altname', u'poi_alt_name', u'poialternatename', u'poi_alternamename', u'poi_altername_name', u'altnames', u'alt_names', u'alternatenames', u'altername_names', u'poialtnames', u'poi_altnames', u'poi_alt_names', u'poialternatenames', u'poi_alternamenames', u'poi_altername_names'],
    u'poidesc': [u'poi_desc', u'description', u'poi_description'],
    u'poifeattype': [u'poi_feat_type', u'poi_feature_type', u'poifeaturetype', u'feat_type', u'feature_type', u'featuretype', u'poifeattyp'],
    u'poilabel': [u'poi_label', u'label', u'poiname', u'poi_name', u'name'],
    u'poiname': [u'poi_name', u'name'],
    u'poitype': [u'poi_type', u'type']
}

valuemap = {
    u'poifeattype': {
        u'entrance': {u'entrance': u'yes'},
        u'entrance point': {u'entrance': u'yes'}
    },
    u'poitype': {
        u'academy': {u'building': u'school'},
        u'accessible': {u'wheelchair': u'yes'},
        u'acme': {u'natural': u'peak'},
        u'adit': {u'man_made': u'mineshaft'},
        u'admin office': {u'office': u'government'},
        u'administrative office': {u'office': u'government'},
        u'ahu': {u'natural': u'peak'},
        u'aiguille': {u'natural': u'peak'},
        u'airport': {u'aeroway': u'aerodrome'},
        u'airstrip': {u'aeroway': u'aerodrome', u'aerodrome': u'airstrip'},
        u'all-terrain vehicle trail': {u'atv': u'yes', u'highway': u'track'},
        u'alp': {u'natural': u'peak'},
        u'alpine': {u'piste:type': u'downhill'},
        u'alpine hut': {u'tourism': u'alpine_hut'},
        u'alpine ski': {u'piste:type': u'downhill'},
        u'alpine ski trail': {u'piste:type': u'downhill'},
        u'amphitheater': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'anchorage': {u'seamark:type': u'anchorage'},
        u'apartment': {u'building': u'apartments'},
        u'apartment building': {u'building': u'apartments'},
        u'apartments': {u'building': u'apartments'},
        u'arch': {u'natural': u'arch'},
        u'archipelago': {u'place': u'island'},
        u'area': {u'place': u'locality'},
        u'arm': {u'natural': u'bay'},
        u'arroyo': {u'waterway': u'drain', u'intermittent': u'yes'},
        u'atm': {u'amenity': u'atm'},
        u'atoll': {u'place': u'island'},
        u'attraction': {u'information': u'exhibit', u'tourism': u'information'},
        u'atv trail': {u'atv': u'yes', u'highway': u'track'},
        u'automated teller machine': {u'amenity': u'atm'},
        u'backcountry office': {u'amenity': u'ranger_station'},
        u'backcountry ski': {u'piste:type': u'skitour'},
        u'backcountry ski trail': {u'piste:type': u'skitour'},
        u'backwater': {u'water': u'lake', u'natural': u'water'},
        u'badge': {u'amenity': u'police'},
        u'bald': {u'natural': u'peak'},
        u'barn': {u'building': u'barn'},
        u'barranca': {u'natural': u'valley'},
        u'basin': {u'landuse': u'basin'},
        u'bath': {u'amenity': u'shower'},
        u'bathroom': {u'amenity': u'toilets'},
        u'battlefield': {u'historic': u'battlefield'},
        u'battlefield marker': {u'historic': u'marker', u'marker_type': u'battlefield'},
        u'bay': {u'natural': u'bay'},
        u'beach': {u'natural': u'beach'},
        u'beck': {u'waterway': u'stream'},
        u'bench': {u'amenity': u'bench'},
        u'berg': {u'natural': u'peak'},
        u'bicycle': {u'bicycle': u'yes', u'highway': u'path'},
        u'bicycle trail': {u'bicycle': u'yes', u'highway': u'path'},
        u'bight': {u'natural': u'bay'},
        u'bike rack': {u'amenity': u'bicycle_parking', u'bicycle_parking': u'rack'},
        u'biodiesel': {u'amenity': u'fuel'},
        u'blind alley': {u'highway': u'turning_circle'},
        u'bluff': {u'natural': u'cliff'},
        u'boat launch': {u'leisure': u'slipway'},
        u'boat ramp': {u'leisure': u'slipway'},
        u'bog': {u'wetland': u'swamp', u'natural': u'wetland'},
        u'bottle': {u'amenity': u'recycling'},
        u'branch': {u'waterway': u'stream'},
        u'breakwater': {u'waterway': u'dam'},
        u'bridge': {u'bridge': u'yes'},
        u'bridleway': {u'leisure': u'horse_riding'},
        u'brochure box': {u'information': u'brochure', u'tourism': u'information'},
        u'brook': {u'waterway': u'stream'},
        u'building': {u'building': u'yes'},
        u'building under construction': {u'building': u'construction'},
        u'bulletin board': {u'information': u'board', u'tourism': u'information'},
        u'bunker': {u'building': u'bunker'},
        u'buoy': {u'man_made': u'buoy'},
        u'burn': {u'waterway': u'stream'},
        u'bus station': {u'highway': u'bus_stop'},
        u'bus stop': {u'highway': u'bus_stop'},
        u'bus stop / shuttle stop': {u'highway': u'bus_stop'},
        u'butte': {u'natural': u'peak'},
        u'cabin': {u'building': u'cabin'},
        u'cafe': {u'amenity': u'food_court'},
        u'caldera': {u'natural': u'volcano'},
        u'camp_site': {u'caravans': u'yes', u'tourism': u'camp_site'},
        u'campfire': {u'leisure': u'firepit'},
        u'campfire ring': {u'leisure': u'firepit'},
        u'campground': {u'tourism': u'camp_site'},
        u'campsite': {u'tourism': u'camp_site', u'camp_site': u'pitch'},
        u'can': {u'amenity': u'recycling'},
        u'canal': {u'waterway': u'canal'},
        u'cannon': {u'historic': u'cannon'},
        u'canoe': {u'leisure': u'slipway', u'canoe': u'yes'},
        u'canoe / kayak access': {u'leisure': u'slipway', u'canoe': u'yes'},
        u'canoe access': {u'leisure': u'slipway', u'canoe': u'yes'},
        u'canyoneering route': {u'sport': u'canyoning', u'highway': u'path'},
        u'car park': {u'amenity': u'parking'},
        u'car parking': {u'amenity': u'parking'},
        u'cascade': {u'waterway': u'waterfall'},
        u'cash dispenser': {u'amenity': u'atm'},
        u'castle': {u'man_made': u'tower'},
        u'cataract': {u'waterway': u'waterfall'},
        u'cathedral': {u'building': u'cathedral'},
        u'cave': {u'natural': u'cave_entrance'},
        u'cave entrance': {u'natural': u'cave_entrance'},
        u'cavern': {u'natural': u'cave_entrance'},
        u'cay': {u'place': u'island'},
        u'cemetery': {u'landuse': u'cemetery'},
        u'cemetery / graveyard': {u'landuse': u'cemetery'},
        u'cerro': {u'natural': u'peak'},
        u'channel': {u'natural': u'strait'},
        u'chapel': {u'building': u'chapel'},
        u'chasm': {u'natural': u'valley'},
        u'church': {u'building': u'church'},
        u'cienega': {u'wetland': u'swamp', u'natural': u'wetland'},
        u'cinder cone': {u'natural': u'volcano'},
        u'cirque': {u'landuse': u'basin'},
        u'city': {u'place': u'hamlet'},
        u'civic': {u'building': u'public'},
        u'civil service': {u'office': u'government'},
        u'cliff': {u'natural': u'cliff'},
        u'climax': {u'natural': u'peak'},
        u'climbing route': {u'sport': u'climbing', u'highway': u'path'},
        u'clinic': {u'amenity': u'hospital'},
        u'cng': {u'amenity': u'fuel'},
        u'coast': {u'natural': u'beach'},
        u'col': {u'natural': u'saddle'},
        u'colina': {u'natural': u'peak'},
        u'college': {u'building': u'university'},
        u'commercial': {u'building': u'commercial'},
        u'commercial building': {u'building': u'commercial'},
        u'composite': {u'natural': u'volcano'},
        u'composite volcano': {u'natural': u'volcano'},
        u'compressed natural gas': {u'amenity': u'fuel'},
        u'cone': {u'natural': u'peak'},
        u'constable': {u'amenity': u'police'},
        u'construction': {u'building': u'construction'},
        u'cops': {u'amenity': u'police'},
        u'coulee': {u'waterway': u'drain', u'intermittent': u'yes'},
        u'course': {u'waterway': u'stream'},
        u'court house': {u'building': u'public'},
        u'crag': {u'natural': u'cliff'},
        u'crater': {u'natural': u'volcano'},
        u'creek': {u'waterway': u'stream'},
        u'cross-country': {u'piste:type': u'nordic'},
        u'cross-country ski': {u'piste:type': u'nordic'},
        u'cross-country ski trail': {u'piste:type': u'nordic'},
        u'crown': {u'natural': u'peak'},
        u'cuesta': {u'natural': u'ridge'},
        u'cul-de-sac': {u'highway': u'turning_circle'},
        u'cumbre': {u'natural': u'peak'},
        u'curling': {u'leisure': u'ice_rink'},
        u'current': {u'waterway': u'stream'},
        u'dam': {u'waterway': u'dam'},
        u'dead end street': {u'highway': u'turning_circle'},
        u'desert': {u'natural': u'desert'},
        u'detached': {u'building': u'detached'},
        u'detached building': {u'building': u'detached'},
        u'detached home': {u'building': u'detached'},
        u'detective': {u'amenity': u'police'},
        u'diesel': {u'amenity': u'fuel'},
        u'dike': {u'waterway': u'dam'},
        u'directional sign': {u'information': u'sign', u'sign:type': u'directional', u'tourism': u'information'},
        u'ditch': {u'waterway': u'canal'},
        u'doctor': {u'amenity': u'hospital'},
        u'dog sled': {u'piste:type': u'sleigh'},
        u'dog sled trail': {u'piste:type': u'sleigh'},
        u'dome': {u'natural': u'peak'},
        u'dorm': {u'building': u'dormitory'},
        u'dormatorium': {u'building': u'dormitory'},
        u'dormitory': {u'building': u'dormitory'},
        u'downhill': {u'piste:type': u'downhill'},
        u'downhill ski': {u'piste:type': u'downhill'},
        u'downhill ski trail': {u'piste:type': u'downhill'},
        u'drift': {u'waterway': u'stream'},
        u'drinking water': {u'amenity': u'drinking_water'},
        u'dump station': {u'amenity': u'sanitary_dump_station'},
        u'dumpstation': {u'amenity': u'sanitary_dump_station'},
        u'dumpster': {u'amenity': u'waste_disposal'},
        u'dune': {u'natural': u'dune'},
        u'dyke': {u'man_made': u'dyke'},
        u'dyke (levee)': {u'man_made': u'dyke'},
        u'earthworks': {u'historic': u'archaeological_site', u'site_type': u'fortification'},
        u'education center': {u'building': u'yes', u'amenity': u'education_centre'},
        u'electric vehicle parking': {u'amenity': u'parking', u'capacity:charging': u'yes'},
        u'elementary school': {u'building': u'school'},
        u'emergency phone': {u'emergency': u'phone'},
        u'emergency room': {u'amenity': u'hospital'},
        u'emergency telephone': {u'emergency': u'phone'},
        u'entrance': {u'barrier': u'entrance'},
        u'entrance station': {u'barrier': u'entrance'},
        u'entry': {u'barrier': u'entrance'},
        u'equestrian': {u'leisure': u'horse_riding'},
        u'equestrian trail': {u'leisure': u'horse_riding'},
        u'escarpment': {u'natural': u'ridge'},
        u'estuary': {u'natural': u'bay'},
        u'exhibit': {u'information': u'exhibit', u'tourism': u'information'},
        u'exhibit / wayside': {u'information': u'exhibit', u'tourism': u'information'},
        u'falls': {u'waterway': u'waterfall'},
        u'fed': {u'amenity': u'police'},
        u'fee': {u'barrier': u'toll_booth'},
        u'fee booth': {u'barrier': u'toll_booth'},
        u'fence': {u'barrier': u'fence'},
        u'ferry terminal': {u'amenity': u'ferry_terminal'},
        u'fin': {u'natural': u'rock'},
        u'fire department': {u'amenity': u'fire_station'},
        u'fire ring': {u'leisure': u'firepit'},
        u'fire station': {u'amenity': u'fire_station'},
        u'firepit': {u'leisure': u'firepit'},
        u'fireplace': {u'leisure': u'firepit'},
        u'first aid': {u'amenity': u'first_aid'},
        u'first aid station': {u'amenity': u'first_aid'},
        u'fish cleaning': {u'amenity': u'fish_cleaning'},
        u'fish hatchery': {u'landuse': u'aquaculture'},
        u'fishing': {u'leisure': u'fishing'},
        u'flag pole': {u'man_made': u'flagpole'},
        u'flagpole': {u'man_made': u'flagpole'},
        u'floating restroom': {u'amenity': u'toilets', u'type': u'floating'},
        u'flood': {u'waterway': u'stream'},
        u'fold': {u'natural': u'rock'},
        u'food box': {u'storage': u'food'},
        u'food box / food cache': {u'storage': u'food'},
        u'food cache': {u'storage': u'food'},
        u'food court': {u'amenity': u'food_court'},
        u'food service': {u'amenity': u'food_court'},
        u'footpath': {u'highway': u'path'},
        u'forest': {u'landuse': u'forest'},
        u'formation': {u'natural': u'rock'},
        u'fort': {u'historic': u'archaeological_site', u'site_type': u'fortification'},
        u'fortification': {u'historic': u'archaeological_site', u'site_type': u'fortification'},
        u'fountain': {u'amenity': u'fountain'},
        u'four-wheel drive trail': {u'4wd_only': u'yes', u'highway': u'track'},
        u'freshet': {u'waterway': u'stream'},
        u'fuel': {u'amenity': u'fuel'},
        u'fumarole': {u'natural': u'volcano'},
        u'gap': {u'natural': u'saddle'},
        u'garage': {u'building': u'garage'},
        u'garden': {u'leisure': u'garden'},
        u'gas station': {u'amenity': u'fuel'},
        u'gate': {u'barrier': u'gate'},
        u'gateway': {u'barrier': u'entrance'},
        u'gateway sign': {u'information': u'sign', u'tourism': u'information'},
        u'gazebo': {u'building': u'pavilion', u'amenity': u'shelter', u'pavilion_type': u'gazebo'},
        u'general store': {u'shop': u'general'},
        u'geyser': {u'natural': u'geyser'},
        u'glacier': {u'natural': u'glacier'},
        u'glasshouse': {u'building': u'greenhouse'},
        u'glen': {u'natural': u'valley'},
        u'golf course': {u'leisure': u'golf_course'},
        u'gorge': {u'natural': u'valley'},
        u'government': {u'office': u'government'},
        u'government headquarters': {u'building': u'office', u'function': u'headquarters', u'office': u'government'},
        u'government office': {u'building': u'office', u'function': u'headquarters', u'office': u'government'},
        u'grassland': {u'natural': u'grassland'},
        u'grave': {u'cemetery': u'grave'},
        u'graveyard': {u'landuse': u'cemetery'},
        u'greenhouse': {u'building': u'greenhouse'},
        u'grill': {u'barbecue_grill': u'yes'},
        u'grotto': {u'natural': u'cave_entrance'},
        u'guide post': {u'information': u'guidepost', u'tourism': u'information'},
        u'guidepost': {u'information': u'guidepost', u'tourism': u'information'},
        u'gulch': {u'natural': u'valley'},
        u'gully': {u'waterway': u'drain', u'intermittent': u'yes'},
        u'gusher': {u'natural': u'geyser'},
        u'hamlet': {u'place': u'hamlet'},
        u'hammock': {u'place': u'island'},
        u'harbor': {u'harbour': u'yes'},
        u'headland': {u'natural': u'cliff'},
        u'headquarters': {u'building': u'office', u'function': u'headquarters', u'office': u'government'},
        u'health service': {u'amenity': u'hospital'},
        u'high school': {u'building': u'school'},
        u'highland': {u'natural': u'grassland'},
        u'hike': {u'highway': u'path'},
        u'hiking': {u'highway': u'path'},
        u'hill': {u'natural': u'peak'},
        u'hill fort': {u'historic': u'archaeological_site', u'site_type': u'fortification'},
        u'historic building': {u'building': u'yes', u'historic': u'building'},
        u'historic cabin': {u'building': u'cabin', u'historic': u'yes'},
        u'historic marker': {u'historic': u'marker'},
        u'historic memorial': {u'historic': u'memorial'},
        u'historic mine': {u'historic': u'mine'},
        u'historic monument': {u'historic': u'monument'},
        u'historic ruins': {u'historic': u'ruins'},
        u'historic ship': {u'historic': u'ship'},
        u'historic site': {u'historic': u'yes'},
        u'hockey': {u'leisure': u'ice_rink'},
        u'hogback': {u'natural': u'ridge'},
        u'hole': {u'landuse': u'basin'},
        u'hollow': {u'natural': u'valley'},
        u'hoodoo': {u'natural': u'rock'},
        u'horn': {u'natural': u'peak'},
        u'horse': {u'leisure': u'horse_riding'},
        u'horse camp': {u'horse': u'yes', u'tourism': u'camp_site'},
        u'horse campground': {u'horse': u'yes', u'tourism': u'camp_site'},
        u'horse riding': {u'leisure': u'horse_riding'},
        u'horseback': {u'leisure': u'horse_riding'},
        u'horseback riding': {u'leisure': u'horse_riding'},
        u'hospital': {u'amenity': u'hospital'},
        u'hospital grounds': {u'amenity': u'hospital'},
        u'hot spring': {u'natural': u'geyser'},
        u'hotel': {u'tourism': u'hotel'},
        u'house': {u'building': u'house'},
        u'hummock': {u'place': u'island'},
        u'hut': {u'building': u'hut'},
        u'ice patch': {u'natural': u'glacier'},
        u'ice rink': {u'leisure': u'ice_rink'},
        u'icefield': {u'natural': u'glacier'},
        u'industrial': {u'building': u'industrial'},
        u'industrial building': {u'building': u'industrial'},
        u'infirmary': {u'amenity': u'hospital'},
        u'information': {u'tourism': u'information'},
        u'information board': {u'information': u'board', u'tourism': u'information'},
        u'information map': {u'information': u'map', u'tourism': u'information'},
        u'inlet': {u'natural': u'bay'},
        u'institution': {u'amenity': u'hospital'},
        u'internet': {u'wifi': u'yes'},
        u'interpretive exhibit': {u'information': u'exhibit', u'tourism': u'information'},
        u'interpretive sign': {u'information': u'exhibit', u'tourism': u'information'},
        u'isla': {u'place': u'island'},
        u'island': {u'place': u'island'},
        u'isle': {u'place': u'island'},
        u'islet': {u'place': u'island'},
        u'isthmus': {u'natural': u'isthmus'},
        u'jetty': {u'waterway': u'dam'},
        u'jumble': {u'natural': u'lava'},
        u'kayak': {u'leisure': u'slipway', u'canoe': u'yes'},
        u'kepula': {u'natural': u'lava'},
        u'key': {u'place': u'island'},
        u'knob': {u'natural': u'peak'},
        u'knoll': {u'natural': u'peak'},
        u'kula': {u'natural': u'grassland'},
        u'lac': {u'water': u'lake', u'natural': u'water'},
        u'lae': {u'natural': u'ridge'},
        u'lagoon': {u'water': u'lake', u'natural': u'water'},
        u'laguna': {u'water': u'lake', u'natural': u'water'},
        u'lake': {u'water': u'lake', u'natural': u'water'},
        u'lakelet': {u'water': u'lake', u'natural': u'water'},
        u'land bridge': {u'natural': u'arch'},
        u'landing': {u'aeroway': u'aerodrome', u'surface': u'ground', u'aerodrome': u'airstrip'},
        u'landing field': {u'aeroway': u'aerodrome', u'aerodrome': u'airstrip'},
        u'landing strip': {u'aeroway': u'aerodrome', u'surface': u'ground', u'aerodrome': u'airstrip'},
        u'lateal': {u'waterway': u'canal'},
        u'latrine': {u'amenity': u'toilets'},
        u'laundry': {u'shop': u'laundry'},
        u'lava': {u'natural': u'lava'},
        u'lava bed': {u'natural': u'lava'},
        u'lava flow': {u'natural': u'lava'},
        u'lavatory': {u'amenity': u'toilets'},
        u'law enforcement': {u'amenity': u'police'},
        u'lea': {u'natural': u'cape'},
        u'letter': {u'amenity': u'post_office'},
        u'levee': {u'man_made': u'dyke'},
        u'lighthouse': {u'man_made': u'lighthouse'},
        u'liquified natural gas': {u'amenity': u'fuel'},
        u'litter': {u'amenity': u'waste_basket'},
        u'litter receptacle': {u'amenity': u'waste_basket'},
        u'lng': {u'amenity': u'fuel'},
        u'locale': {u'place': u'locality'},
        u'locality': {u'place': u'locality'},
        u'loch': {u'water': u'lake', u'natural': u'water'},
        u'lock': {u'lock': u'yes'},
        u'lodge': {u'tourism': u'alpine_hut'},
        u'lodging': {u'tourism': u'hotel'},
        u'mail': {u'amenity': u'post_office'},
        u'mail office': {u'amenity': u'post_office'},
        u'mailbox': {u'amenity': u'post_box'},
        u'map': {u'information': u'map', u'tourism': u'information'},
        u'marais': {u'wetland': u'swamp', u'natural': u'wetland'},
        u'marina': {u'leisure': u'marina'},
        u'marker': {u'information': u'guidepost', u'tourism': u'information'},
        u'marsh': {u'wetland': u'swamp', u'natural': u'wetland'},
        u'mauna': {u'natural': u'peak'},
        u'memorial': {u'historic': u'memorial'},
        u'mere': {u'water': u'lake', u'natural': u'water'},
        u'mesa': {u'natural': u'peak'},
        u'mesita': {u'natural': u'peak'},
        u'metro stop': {u'railway': u'subway_entrance'},
        u'metro stop / subway entrance': {u'railway': u'subway_entrance'},
        u'middle school': {u'building': u'school'},
        u'mile marker': {u'highway': u'milestone'},
        u'military area': {u'landuse': u'military'},
        u'military bunker': {u'building': u'bunker'},
        u'mineshaft': {u'man_made': u'mineshaft'},
        u'mobile home': {u'building': u'static_caravan'},
        u'moku': {u'place': u'island'},
        u'monument': {u'historic': u'monument'},
        u'mooring': {u'mooring': u'yes'},
        u'motel': {u'tourism': u'hotel'},
        u'motorcycle': {u'motorcycle': u'yes', u'highway': u'track'},
        u'motorcycle trail': {u'motorcycle': u'yes', u'highway': u'track'},
        u'motorhome park': {u'caravans': u'yes', u'tourism': u'camp_site'},
        u'motorized trail': {u'highway': u'track'},
        u'mound': {u'natural': u'peak'},
        u'mount': {u'natural': u'peak'},
        u'mountain': {u'natural': u'peak'},
        u'mountain pass (saddle / gap)': {u'natural': u'saddle'},
        u'museum': {u'tourism': u'museum'},
        u'mushing': {u'piste:type': u'sleigh'},
        u'mushing trail': {u'piste:type': u'sleigh'},
        u'musical': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'natural bridge': {u'natural': u'arch'},
        u'nature reserve': {u'leisure': u'nature_reserve'},
        u'neck': {u'natural': u'cape'},
        u'neighborhood': {u'place': u'hamlet'},
        u'nipple': {u'natural': u'rock'},
        u'non-motorized trail': {u'highway': u'path'},
        u'nordic': {u'piste:type': u'nordic'},
        u'nordic ski': {u'piste:type': u'nordic'},
        u'nordic ski trail': {u'piste:type': u'nordic'},
        u'nose': {u'natural': u'cliff'},
        u'notch': {u'natural': u'saddle'},
        u'ocean': {u'place': u'sea'},
        u'office': {u'building': u'office'},
        u'officer': {u'amenity': u'police'},
        u'oilfield': {u'man_made': u'oilfield'},
        u'online': {u'wifi': u'yes'},
        u'opera house': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'outhouse': {u'amenity': u'toilets'},
        u'overlook': {u'viewpoint_type': u'overlook', u'tourism': u'viewpoint'},
        u'package': {u'amenity': u'post_office'},
        u'palisades': {u'natural': u'cliff'},
        u'parcel': {u'amenity': u'post_office'},
        u'parking': {u'amenity': u'parking'},
        u'parking lot': {u'amenity': u'parking'},
        u'pass': {u'natural': u'saddle'},
        u'passage': {u'natural': u'strait'},
        u'patrol cabin': {u'amenity': u'patrol_cabin'},
        u'pavilion': {u'building': u'pavilion', u'amenity': u'shelter'},
        u'peak': {u'natural': u'peak'},
        u'peninsula': {u'natural': u'cape'},
        u'performance': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'permit center': {u'amenity': u'ranger_station'},
        u'permit centre': {u'amenity': u'ranger_station'},
        u'petrol': {u'amenity': u'fuel'},
        u'petrol station': {u'amenity': u'fuel'},
        u'phone booth': {u'amenity': u'telephone'},
        u'picnic area': {u'tourism': u'picnic_site'},
        u'picnic site': {u'tourism': u'picnic_site'},
        u'picnic table': {u'leisure': u'picnic_table'},
        u'pinnacle': {u'natural': u'peak'},
        u'pit': {u'landuse': u'basin'},
        u'place name': {u'information': u'sign', u'tourism': u'information'},
        u'plateau': {u'natural': u'landform', u'landform': u'plateau'},
        u'play': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'playground': {u'leisure': u'playground'},
        u'playhouse': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'pocosin': {u'wetland': u'swamp', u'natural': u'wetland'},
        u'poi': {u'tourism': u'yes'},
        u'point': {u'natural': u'cape'},
        u'point of interest': {u'tourism': u'yes'},
        u'police': {u'amenity': u'police'},
        u'police force': {u'amenity': u'police'},
        u'police station': {u'amenity': u'police'},
        u'pond': {u'water': u'lake', u'natural': u'water'},
        u'pool': {u'water': u'lake', u'natural': u'water'},
        u'populated place': {u'place': u'hamlet'},
        u'portal': {u'barrier': u'entrance'},
        u'post': {u'amenity': u'post_office'},
        u'post office': {u'amenity': u'post_office'},
        u'potable': {u'amenity': u'drinking_water'},
        u'potable water': {u'amenity': u'drinking_water'},
        u'prairie': {u'grassland': u'prarie', u'natural': u'grassland'},
        u'prarie': {u'grassland': u'prarie', u'natural': u'grassland'},
        u'precipice': {u'natural': u'cliff'},
        u'primitive': {u'backcountry': u'yes', u'tourism': u'camp_site', u'camp_site': u'pitch'},
        u'primitive camping': {u'backcountry': u'yes', u'tourism': u'camp_site', u'camp_site': u'pitch'},
        u'privy': {u'amenity': u'toilets'},
        u'promontory': {u'natural': u'cliff'},
        u'propane': {u'amenity': u'fuel'},
        u'protected': {u'leisure': u'nature_reserve'},
        u'protected area': {u'leisure': u'nature_reserve'},
        u'public': {u'building': u'public'},
        u'public building': {u'building': u'public'},
        u'puu': {u'natural': u'peak'},
        u'quarry': {u'landuse': u'quarry'},
        u'quarry (mine)': {u'landuse': u'quarry'},
        u'race': {u'waterway': u'stream'},
        u'radiator water': {u'emergency': u'water_tank'},
        u'raft': {u'leisure': u'slipway', u'canoe': u'yes'},
        u'railway station': {u'building': u'train_station'},
        u'ranger station': {u'amenity': u'ranger_station'},
        u'rapids': {u'waterway': u'rapids'},
        u'rass': {u'natural': u'cape'},
        u'ravine': {u'natural': u'valley'},
        u'reach': {u'natural': u'strait'},
        u'recycling': {u'amenity': u'recycling'},
        u'reef (bar)': {u'natural': u'reef'},
        u'register': {u'tourism': u'register'},
        u'regulatory sign': {u'information': u'sign', u'sign:type': u'regulatory', u'tourism': u'information'},
        u'resaca': {u'water': u'lake', u'natural': u'water'},
        u'reserve': {u'leisure': u'nature_reserve'},
        u'reservoir': {u'water': u'reservoir', u'landuse': u'reservoir', u'natural': u'water'},
        u'residence hall': {u'building': u'dormitory'},
        u'residential': {u'building': u'residential'},
        u'residential building': {u'building': u'residential'},
        u'resort': {u'tourism': u'hotel'},
        u'restaurant': {u'amenity': u'food_court'},
        u'restroom': {u'amenity': u'toilets'},
        u'retail': {u'building': u'retail'},
        u'retail building': {u'building': u'retail'},
        u'ridge': {u'natural': u'ridge'},
        u'riffle': {u'waterway': u'rapids'},
        u'rill': {u'waterway': u'stream'},
        u'rimrock': {u'natural': u'cliff'},
        u'rindle': {u'waterway': u'stream'},
        u'ripple': {u'waterway': u'rapids'},
        u'rivulet': {u'waterway': u'stream'},
        u'roadside pullout': {u'highway': u'rest_area'},
        u'rock formation': {u'natural': u'rock'},
        u'row house': {u'building': u'terrace'},
        u'rubbish': {u'amenity': u'waste_basket'},
        u'ruins': {u'historic': u'ruins'},
        u'run': {u'waterway': u'stream'},
        u'runnel': {u'waterway': u'stream'},
        u'rush': {u'waterway': u'stream'},
        u'rv campground': {u'caravans': u'yes', u'tourism': u'camp_site'},
        u'saddle': {u'natural': u'saddle'},
        u'sailing': {u'sport': u'sailing'},
        u'salvage': {u'amenity': u'recycling'},
        u'sand dune': {u'natural': u'dune'},
        u'sanitary disposal station': {u'amenity': u'sanitary_dump_station'},
        u'scenery': {u'tourism': u'viewpoint'},
        u'scenic': {u'tourism': u'viewpoint'},
        u'scenic overlook': {u'viewpoint_type': u'overlook', u'tourism': u'viewpoint'},
        u'scenic viewpoint': {u'tourism': u'viewpoint'},
        u'school': {u'building': u'school'},
        u'school building': {u'building': u'school'},
        u'scrap': {u'amenity': u'recycling'},
        u'scuba diving': {u'sport': u'scuba_diving'},
        u'sculpture': {u'artwork_type': u'statue', u'tourism': u'artwork'},
        u'sea': {u'place': u'sea'},
        u'sea arch': {u'natural': u'arch'},
        u'seat': {u'amenity': u'bench'},
        u'seep': {u'natural': u'spring'},
        u'self guiding trail': {u'information': u'guidepost', u'tourism': u'information'},
        u'shaft': {u'man_made': u'mineshaft'},
        u'shaft (mine)': {u'man_made': u'mineshaft'},
        u'shed': {u'building': u'shed'},
        u'shelter': {u'building': u'hut', u'amenity': u'shelter'},
        u'shield': {u'natural': u'volcano'},
        u'shield volcano': {u'natural': u'volcano'},
        u'ship': {u'historic': u'ship'},
        u'shipwreck': {u'historic': u'wreck'},
        u'shoal (bar)': {u'natural': u'shoal'},
        u'shop': {u'shop': u'general'},
        u'shore': {u'natural': u'beach'},
        u'shower': {u'amenity': u'shower'},
        u'showers': {u'amenity': u'shower'},
        u'shuttle stop': {u'highway': u'bus_stop'},
        u'sick': {u'amenity': u'hospital'},
        u'sink': {u'landuse': u'basin'},
        u'sinkhole': {u'landuse': u'basin'},
        u'site': {u'historic': u'yes'},
        u'skating': {u'leisure': u'ice_rink'},
        u'sled': {u'piste:type': u'sled'},
        u'sledding': {u'piste:type': u'sled'},
        u'slickrock': {u'natural': u'rock'},
        u'slide': {u'natural': u'rock'},
        u'slipway': {u'leisure': u'slipway'},
        u'slope': {u'natural': u'cliff'},
        u'snack bar': {u'amenity': u'food_court'},
        u'snow machine': {u'snowmobile': u'yes', u'highway': u'track'},
        u'snow patch': {u'natural': u'glacier'},
        u'snowmobile': {u'snowmobile': u'yes', u'highway': u'track'},
        u'snowmobile trail': {u'snowmobile': u'yes', u'highway': u'track'},
        u'snowshoe': {u'piste:type': u'hike'},
        u'snowshoe trail': {u'piste:type': u'hike'},
        u'sound': {u'natural': u'bay'},
        u'spate': {u'waterway': u'stream'},
        u'spire': {u'natural': u'rock'},
        u'spout': {u'natural': u'geyser'},
        u'spring': {u'natural': u'spring'},
        u'spritz': {u'waterway': u'stream'},
        u'spur': {u'natural': u'ridge'},
        u'stable': {u'building': u'stable'},
        u'staircase': {u'highway': u'steps'},
        u'static caravan': {u'building': u'static_caravan'},
        u'static mobile home': {u'building': u'static_caravan'},
        u'steps': {u'highway': u'steps'},
        u'stop light': {u'highway': u'traffic_signals'},
        u'stoplight': {u'highway': u'traffic_signals'},
        u'storage': {u'building': u'warehouse'},
        u'store': {u'shop': u'general'},
        u'strait': {u'natural': u'strait'},
        u'strait (channel)': {u'natural': u'strait'},
        u'strand': {u'natural': u'beach'},
        u'stream': {u'waterway': u'stream'},
        u'subway entrance': {u'railway': u'subway_entrance'},
        u'subway exit': {u'railway': u'subway_entrance'},
        u'sugarload': {u'natural': u'peak'},
        u'summit': {u'natural': u'peak'},
        u'surge': {u'waterway': u'stream'},
        u'surgery': {u'amenity': u'hospital'},
        u'swamp': {u'wetland': u'swamp', u'natural': u'wetland'},
        u'swimming area': {u'sport': u'swimming'},
        u'table': {u'natural': u'peak'},
        u'tank': {u'water': u'reservoir', u'landuse': u'reservoir', u'natural': u'water'},
        u'telephone': {u'amenity': u'telephone'},
        u'telephone box': {u'amenity': u'telephone'},
        u'terrace': {u'building': u'terrace'},
        u'theater': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'theatre': {u'amenity': u'theatre', u'theatre:type': u'amphi'},
        u'thermal geyser': {u'natural': u'geyser'},
        u'thermal spring': {u'natural': u'geyser'},
        u'thoroughfare': {u'natural': u'strait'},
        u'throne': {u'natural': u'rock'},
        u'throughfare': {u'natural': u'strait'},
        u'tide': {u'waterway': u'stream'},
        u'tip': {u'natural': u'peak'},
        u'toilet': {u'amenity': u'toilets'},
        u'toilets': {u'amenity': u'toilets'},
        u'toll': {u'barrier': u'toll_booth'},
        u'toll booth': {u'barrier': u'toll_booth'},
        u'tomb': {u'cemetery': u'grave'},
        u'top': {u'natural': u'peak'},
        u'tornado shelter': {u'amenity': u'shelter'},
        u'torrent': {u'waterway': u'stream'},
        u'tourist attraction': {u'information': u'exhibit', u'tourism': u'information'},
        u'tourist information': {u'tourism': u'information'},
        u'tower': {u'man_made': u'tower'},
        u'town': {u'place': u'hamlet'},
        u'town hall': {u'building': u'public'},
        u'townhouse': {u'building': u'terrace'},
        u'trackway': {u'highway': u'path'},
        u'traffic light': {u'highway': u'traffic_signals'},
        u'traffic signal': {u'highway': u'traffic_signals'},
        u'traffic signals': {u'highway': u'traffic_signals'},
        u'trail marker': {u'information': u'guidepost', u'tourism': u'information'},
        u'trail register': {u'tourism': u'register'},
        u'trail sign': {u'information': u'sign', u'sign:type': u'trail_sign', u'tourism': u'information'},
        u'trailhead': {u'highway': u'trailhead'},
        u'train station': {u'building': u'train_station'},
        u'trash bin': {u'amenity': u'waste_basket'},
        u'tree': {u'natural': u'tree'},
        u'trench': {u'historic': u'archaeological_site', u'site_type': u'fortification'},
        u'tributary': {u'waterway': u'stream'},
        u'tunnel': {u'tunnel': u'yes'},
        u'turning circle': {u'highway': u'turning_circle'},
        u'under construction': {u'building': u'construction'},
        u'university': {u'building': u'university'},
        u'university building': {u'building': u'university'},
        u'upland': {u'natural': u'grassland'},
        u'valley': {u'natural': u'valley'},
        u'vehicle parking': {u'amenity': u'parking'},
        u'viewpoint': {u'tourism': u'viewpoint'},
        u'visitor center': {u'information': u'office', u'tourism': u'information'},
        u'visitor centre': {u'information': u'office', u'tourism': u'information'},
        u'visitor information': {u'information': u'office', u'tourism': u'information'},
        u'volcano': {u'natural': u'volcano'},
        u'walk': {u'highway': u'path'},
        u'wall': {u'natural': u'rock'},
        u'ward': {u'amenity': u'hospital'},
        u'warden center': {u'amenity': u'ranger_station'},
        u'warden office': {u'amenity': u'ranger_station'},
        u'warehouse': {u'building': u'warehouse'},
        u'wash': {u'waterway': u'drain', u'intermittent': u'yes'},
        u'waste basket': {u'amenity': u'waste_basket'},
        u'waste bin': {u'amenity': u'waste_basket'},
        u'waste paper basket': {u'amenity': u'waste_basket'},
        u'water closet': {u'amenity': u'toilets'},
        u'water gap': {u'natural': u'saddle'},
        u'water tank': {u'emergency': u'water_tank'},
        u'water well': {u'man_made': u'water_well'},
        u'watercourse': {u'waterway': u'stream'},
        u'waterfall': {u'waterway': u'waterfall'},
        u'waterhole': {u'water': u'lake', u'natural': u'water'},
        u'wayside': {u'information': u'exhibit', u'tourism': u'information'},
        u'wc': {u'amenity': u'toilets'},
        u'weather shelter': {u'amenity': u'shelter'},
        u'well': {u'amenity': u'fountain'},
        u'wetland': {u'natural': u'wetland'},
        u'wheelchair': {u'wheelchair': u'yes'},
        u'wheelchair accessible': {u'wheelchair': u'yes'},
        u'wi-fi': {u'wifi': u'yes'},
        u'wifi': {u'wifi': u'yes'},
        u'wilderness hut': {u'tourism': u'alpine_hut'},
        u'wildlife': {u'leisure': u'nature_reserve'},
        u'wildlife reserve': {u'leisure': u'nature_reserve'},
        u'wind gap': {u'natural': u'saddle'},
        u'wind surfing area': {u'sport': u'windsurfing'},
        u'windmill': {u'man_made': u'windmill'},
        u'window': {u'natural': u'arch'},
        u'windsurfing area': {u'sport': u'windsurfing'},
        u'winter track': {u'piste:type': u'sleigh'},
        u'woods': {u'natural': u'wood'},
        u'wreck': {u'historic': u'wreck'},
        u'xcs': {u'piste:type': u'nordic'},
        u'zebra mussel decontamination station': {u'amenity': u'boat_wash', u'type': u'zebra_mussel'}
    }
}
