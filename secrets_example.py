"""Defines the names recognized by OsmApiServer

OsmApiServer currently only expects the following properties for a name
 url: the schema and server name where an OSM API exists
 consumer_key: the identification cede for this application on the named server
 consumer_secret: the corresponding secret for the consumer_key

 Currently, only NPS authenticate systems (places, test) are supported, others
 use oauth to authenticate, those will probably require pre-access/caching of
 the access_token and access_token_secret after the users has given permission to
 this consumer.
"""

secrets = {
    'osm': {
        'url': 'http://www.openstreetmap.org',
        'consumer_key': 'XXX',
        'consumer_secret': 'XXX',
        'token': 'XXX',
        'token_secret': 'XXX',
        'npmap_oauth': False
    },
    'places': {
        'url': 'http://10.147.153.193',
        'consumer_key': 'XXX',
        'consumer_secret': 'XXX',
        'npmap_oauth': True
    },
    'test': {
        'url': 'http://10.147.153.193:8000',
        'consumer_key': 'XXX',
        'consumer_secret': 'XXX',
        'npmap_oauth': True
    },
}
