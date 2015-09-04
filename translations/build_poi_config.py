__author__ = 'RESarwas'

"""Build the data for the poi_config.py file based on the source data in a google sheet
This is quick and dirty code, don't expect it to work without some fiddling"""

import requests
import csv
from io import open  # slow but python 3 compatible
import ast


def get_csv_from_google():
    sheet_url = 'http://docs.google.com/spreadsheets/d/1XFqkmIYMEp73q9flgNto9QJim6N5hbacgkUAgdf0rhE/export?format=csv'

    resp = requests.get(sheet_url)
    if resp.status_code != 200:
        print ('server response', sheet_url, resp)
        raise Exception('failed to get data from google docs')
    return csv.DictReader(resp)


def get_csv_from_file():
    sheet_path = r"C:\Users\resarwas\Downloads\NPS_Preset_Classes - Sheet1.csv"

    f = open(sheet_path, 'r', encoding='utf-8')
    return csv.DictReader(f)

# data = get_csv_from_google()
data = get_csv_from_file()
valuemap = {}
synonyms = {}
for row in data:
    if row['point'].lower() == 'x':
        name = row['name'].lower()
        valuemap[name] = ast.literal_eval(row['tags'])
        synonym_set = set()
        altnames = row['altNames']
        if len(altnames) < 2:
            continue
        altnames = altnames[1:][:-1].replace('"', '').split(',')
        for altname in [n.lower() for n in altnames]:
            if altname != name:
                synonym_set.add(altname)
        synonyms[name] = list(synonym_set)
"""
print '\n\nvaluemap\n'
for (k,v) in valuemap.items():
    print k,v

print '\n\nsynonyms\n'
for (k,v) in synonyms.items():
    print k,v
"""
synonym_flip = {}
for (k, v) in synonyms.items():
    for item in v:
        if item not in synonyms:
            try:
                synonym_flip[item].append(k)
            except KeyError:
                synonym_flip[item] = [k]

mylist = []
for (k, v) in synonym_flip.items():
    if len(v) == 1:
        mylist.append((k, v[0]))
"""
print '\n\nunambiguous alternative names\n'
mylist.sort()
for (k, v) in mylist:
    print k,': ', v
"""
ignorelist = []
for (k, v) in synonym_flip.items():
    if len(v) > 1:
        ignorelist.append((k, v))

print '\n\nambiguous alt names\n'
ignorelist.sort()
for (k, v) in ignorelist:
    print k, v

# Add the unambiguous alternative names
for (k, v) in mylist:
    valuemap[k] = valuemap[v]

mynewlist = []
for (k, v) in valuemap.items():
    mynewlist.append((k, v))

mynewlist.sort()
print '\n\nfinal value map\n'
print "    'POITYPE': {"
for (k, v) in mynewlist:
    print "        '{0}': {1},".format(k, v)
print "    },"
