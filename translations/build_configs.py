import requests
import csv
from io import open  # slow but python 3 compatible
import json

__author__ = 'RESarwas'

"""Build the data for the poi_config.py file based on the source data in a google sheet
This is quick and dirty code, don't expect it to work without some fiddling"""


def get_csv_from_google():
    sheet1_url = 'http://docs.google.com/spreadsheets/d/1V8DsAeBipMrll2rmjjTZ6fYTE8g69dI9k6V762K4PYA/export?format=csv'
    # This only downloads the first sheet; use edit mode, and then file, export as csv on the other sheets
    resp = requests.get(sheet1_url)
    if resp.status_code != 200:
        print ('server response', sheet1_url, resp)
        raise Exception('failed to get data from google docs')
    return csv.DictReader(resp)


def get_csv_from_file(name):
    sheet_paths = {
        "translators": r"C:\Users\resarwas\Downloads\arc2places Translator Configurations - Translators.csv",
        "field_maps": r"C:\Users\resarwas\Downloads\arc2places Translator Configurations - Field Mapping.csv",
        "value_maps": r"C:\Users\resarwas\Downloads\arc2places Translator Configurations - Value Mapping.csv",
        "presets": r"C:\Users\resarwas\Downloads\NPS_Preset_Classes - Sheet1.csv"
    }
    f = open(sheet_paths[name], 'r', encoding='utf-8')
    return csv.DictReader(f)


def dict_str_str2str(d, lead='    '):
    result = u'\n'
    if not d:
        return result
    keys = d.keys()
    keys.sort()
    items = []
    for k in keys:
        items.append(lead + u"u'{0}': u'{1}'".format(k, d[k]))
    return result + ',\n'.join(items) + '\n'


def dict_str_list2str(d, lead='    '):
    result = u'\n'
    if not d:
        return result
    keys = d.keys()
    keys.sort()
    items = []
    for k in keys:
        if d[k]:
            items.append(lead + u"u'{0}': {1}".format(k, d[k]))
    return result + ',\n'.join(items) + '\n'


def dict_str_dict_str_dict2str(d, lead='    '):
    result = u'\n'
    if not d:
        return result
    keys = d.keys()
    keys.sort()
    items = []
    for k in keys:
        temp = lead + u"u'{0}'".format(k) + ": {\n"
        subkeys = d[k].keys()
        subkeys.sort()
        subitems = []
        for sk in subkeys:
            subitems.append(lead + lead + u"u'{0}': {1}".format(sk, d[k][sk]))
        items.append(temp + ',\n'.join(subitems) + '\n' + lead + '}')
    return result + ',\n'.join(items) + '\n'


def valuemap_from_presets(translator, field):
    if translator == 'poi' and field == 'poitype':
        return valuemap_from_presets_internal(lambda row: row['point'] == 'x')
    if translator == 'trails' and field == 'trluse':
        return valuemap_from_presets_internal(lambda row: row['superclass'] == 'Trail')


def valuemap_from_presets_internal(selector, lead='    ', debug=False, as_string=False):
    data = get_csv_from_file("presets")
    valuemap = {}
    synonyms = {}
    line = 1  # skip header
    for row in data:
        line += 1
        if selector(row):
            name = row['name'].lower()
            tags = row['tags']
            if not name or not tags:
                continue
            tags = tags.replace('"*"', '"yes"')
            try:
                valuemap[name] = json.loads(tags)
            except ValueError:
                print u"Unable to decode tags for {0} on line {2} of NPS_Preset_Classes".format(name, line)
                continue
            altnames = row['altNames'].lower()
            synonyms[name] = []
            if not altnames:
                continue
            try:
                altnames = json.loads(altnames)
            except (ValueError, IndexError):
                print u"Unable to decode altName for {0} on line {2} of NPS_Preset_Classes".format(name, line)
                continue
            uniquenames = set(altnames)
            if name in uniquenames:
                uniquenames.remove(name)
            synonyms[name] = list(uniquenames)

    if debug:
        print '\n\nvaluemap\n'
        for (k, v) in valuemap.items():
            print k, v

        print '\n\nsynonyms\n'
        for (k, v) in synonyms.items():
            print k, v

    synonym_flip = {}
    for (k, v) in synonyms.items():
        for item in v:
            if item not in synonyms:
                try:
                    synonym_flip[item].append(k)
                except KeyError:
                    synonym_flip[item] = [k]

    unambiguous_altnames = []
    for (k, v) in synonym_flip.items():
        if len(v) == 1:
            unambiguous_altnames.append((k, v[0]))
    # Add the unambiguous alternative names
    for (k, v) in unambiguous_altnames:
        valuemap[k] = valuemap[v]

    if debug:
        print '\n\nunambiguous alternative names\n'
        unambiguous_altnames.sort()
        for (k, v) in unambiguous_altnames:
            print k, ': ', v

        print '\n\nambiguous alt names\n'
        ambiguous_altnames = []
        for (k, v) in synonym_flip.items():
            if len(v) > 1:
                ambiguous_altnames.append((k, v))
        ambiguous_altnames.sort()
        for (k, v) in ambiguous_altnames:
            print k, v

    if as_string:
        mynewlist = []
        for (k, v) in valuemap.items():
            mynewlist.append((k, v))
        mynewlist.sort()
        items = []
        for (k, v) in mynewlist:
            items.append(lead + lead + u"u'{0}': {1}".format(k, v))
        result = u",\n".join(items)
        result = result.replace("'*'", "'yes'")
        if debug:
            print result
        return result
    else:  # as dictionary
        return valuemap


# Translators
def get_translators_list():
    _translators = []
    for row in get_csv_from_file("translators"):
        translator = row['Name'].lower()
        if translator:
            _translators.append(translator)
    return _translators


# Defaults
def get_defaults_dict():
    _defaults = {}
    line = 1  # skip header
    for row in get_csv_from_file("translators"):
        line += 1
        translator = row['Name'].lower()
        tags = row['Default Tags']
        if not translator or not tags:
            continue
        if tags:
            try:
                _defaults[translator] = json.loads(tags)
            except ValueError:
                print u"Unable to decode Default Tags for {0} on line {1} of Translators sheet".format(translator, line)
    return _defaults


# Field Maps
def get_fieldmap_dict():
    _fieldmap = {}
    for row in get_csv_from_file("field_maps"):
        translator = row['Translator'].lower()
        field = row['GIS Field Name'].lower()
        tags = row['Places Tag Name']
        if not translator or not field or not tags:
            continue
        if translator not in _fieldmap:
            _fieldmap[translator] = {}
        _fieldmap[translator][field] = tags
    return _fieldmap


# Alt Names
def get_altnames_dict():
    _altnames = {}
    line = 1  # skip header
    for row in get_csv_from_file("field_maps"):
        line += 1
        translator = row['Translator'].lower()
        field = row['GIS Field Name'].lower()
        altnamelist = row['Alternate GIS Names'].lower()
        if not translator or not field or not altnamelist:
            continue
        if translator not in _altnames:
            _altnames[translator] = {}
        try:
            _altnames[translator][field] = json.loads(altnamelist)
        except ValueError:
            print u"Unable to decode Alternate GIS Names for {0} in {1} on line {2} of Field Mapping sheet".format(
                field, translator, line)
    return _altnames


# Value Maps
def get_valuemap_dict():
    _valuemap = {}
    line = 1  # skip header
    for row in get_csv_from_file("value_maps"):
        line += 1
        translator = row['Translator'].lower()
        field = row['GIS Field Name'].lower()
        value = row['GIS Field Value'].lower()
        if not translator or not field or not value:
            continue
        if translator not in _valuemap:
            _valuemap[translator] = {}
        if field not in _valuemap[translator]:
            _valuemap[translator][field] = {}
        if value == '*':
            _valuemap[translator][field] = valuemap_from_presets(translator, field)
            continue
        altvalues = row['Alternate GIS Values'].lower()
        tags = None
        if row['Places Tags']:
            try:
                tags = json.loads(row['Places Tags'])
            except ValueError:
                print u"Unable to decode Places Tags for {0} = {1} in {2} on line {3} of Value Mapping sheet".format(
                    field, value, translator, line)
        if tags is not None:
            _valuemap[translator][field][value] = tags
            if altvalues:
                try:
                    altvalues = json.loads(altvalues)
                except ValueError:
                    altvalues = []
                    print (u"Unable to decode Alternate GIS Values for "
                           u"{0} = {1} in {2} on line {3} of Value Mapping sheet").format(field, value, translator, line)
            for altvalue in altvalues:
                _valuemap[translator][field][altvalue] = tags
    return _valuemap


# Add it all together
def add_it_up(translators):
    defaults = get_defaults_dict()
    fieldmap = get_fieldmap_dict()
    altnames = get_altnames_dict()
    valuemap = get_valuemap_dict()
    results = {}
    for translator in translators:
        results[translator] = u""
        if translator in defaults and defaults[translator]:
            results[translator] += "defaults = {" + dict_str_str2str(defaults[translator]) + "}\n"
        else:
            results[translator] += "defaults = {}\n"
        results[translator] += "\n"
        if translator in fieldmap and fieldmap[translator]:
            results[translator] += "fieldmap = {" + dict_str_str2str(fieldmap[translator]) + "}\n"
        else:
            results[translator] += "fieldmap = {}\n"
        results[translator] += "\n"
        if translator in altnames and altnames[translator]:
            results[translator] += "altnames = {" + dict_str_list2str(altnames[translator]) + "}\n"
        else:
            results[translator] += "altnames = {}\n"
        results[translator] += "\n"
        if translator in valuemap and valuemap[translator]:
            results[translator] += "valuemap = {" + dict_str_dict_str_dict2str(valuemap[translator]) + "}\n"
        else:
            results[translator] += "valuemap = {}\n"
    return results


def print_it():
    translators = get_translators_list()
    results = add_it_up(translators)
    for translator in translators:
        print "\n\n", '#' * 10, translator, '#' * 10, "\n"
        print results[translator]


def save_it():
    translators = get_translators_list()
    results = add_it_up(translators)
    for translator in translators:
        name = "config_{0}.py".format(translator)
        with open(name, 'w', encoding='utf-8') as f:
            f.write(results[translator])


if __name__ == '__main__':
    # print_it()
    save_it()
