import csv
from io import open  # slow but python 3 compatible
import json


def get_csv_from_file(name):
    sheet_paths = {
        "translators": r"C:\Users\resarwas\Downloads\arc2places Translator Configurations - Translators.csv",
        "field_maps": r"C:\Users\resarwas\Downloads\arc2places Translator Configurations - Field Mapping.csv",
        "value_maps": r"C:\Users\resarwas\Downloads\arc2places Translator Configurations - Value Mapping.csv",
        "presets": r"C:\Users\resarwas\Downloads\NPS_Preset_Classes - Sheet1.csv"
    }
    f = open(sheet_paths[name], 'r', encoding='utf-8')
    return csv.DictReader(f)


def valuemap_from_presets_internal(test_unique=False):
    data = get_csv_from_file("presets")
    names = []
    line = 1  # skip header
    for row in data:
        line += 1
        name = row['name'].lower()
        altnames = row['altNames'].lower()
        if not altnames or not name:
            continue
        try:
            # FIXME: convert 'altNames' column to a JSON list
            # TODO: Add all eGIS TRLUSE values to altNames in NPS_Preset_Classes
            # altnames = json.loads(altnames)
            altnames = altnames[1:][:-1].replace('"', '').split(',')
        except (ValueError, IndexError):
            print u"Unable to decode altName for {0} on line {2} of NPS_Preset_Classes".format(name, line)
            continue
        if test_unique:
            uniquenames = set(altnames)
            if len(uniquenames) != len(altnames):
                print "duplicates in {0} on line {1}".format(name,line)
        if name in altnames:
            altnames.remove(name)
        altnames = json.dumps(list(altnames))
        if altnames == '[]':
            altnames = ''
        names.append((line, name, altnames))

    print 'num\tname\taltNames2'
    for (i, n, a) in names:
        print '{0}\t{1}\t{2}'.format(i, n, a)


if __name__ == '__main__':
    valuemap_from_presets_internal()
