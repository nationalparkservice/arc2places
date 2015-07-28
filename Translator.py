__author__ = 'regan'

import os
import json


def get_function(module, name):
    try:
        func = getattr(module, name)
        getattr(func, '__call__')
    except AttributeError:
        func = None
    return func


def set_translators():
    this_module_folder = os.path.dirname(__file__)
    translations_folder = 'translations'
    config_file = 'translators.json'
    config_path = os.path.join(this_module_folder, translations_folder, config_file)
    try:
        with open(config_path) as fp:
            Translator.translators = json.load(fp)
    except (IOError, ValueError):
        # If the file cannot be opened, IOError is raised
        # If the data being deserialized is not a valid JSON document, a ValueError will be raised.
        pass


class Translator:

    translators = {}

    def __init__(self, name, module):
        self.name = name
        self.path = os.path.realpath(module.__file__)
        self.translation_module = module

    def filter_tags(self, tags):
        default = lambda x: x
        func = get_function(self.translation_module, 'filter_tags')
        if func is None:
            func = get_function(self.translation_module, 'filterTags')
        if func is None:
            func = default
        return func(tags)

    def filter_feature(self, feature, fieldnames, reproject):
        default = lambda x, y, z: x
        func = get_function(self.translation_module, 'filter_feature')
        if func is None:
            func = get_function(self.translation_module, 'filterFeature')
        if func is None:
            func = default
        return func(feature, fieldnames, reproject)

    def filter_feature_post(self, feature, arcfeature, arcgeometry):
        default = lambda x, y, z: x
        func = get_function(self.translation_module, 'filter_feature_post')
        if func is None:
            func = get_function(self.translation_module, 'filterFeaturePost')
        if func is None:
            func = default
        return func(feature, arcfeature, arcgeometry)

    def transform_pre_output(self, geometries, features):
        default = lambda x, y: None
        func = get_function(self.translation_module, 'transform_pre_output')
        if func is None:
            func = get_function(self.translation_module, 'preOutputTransform')
        if func is None:
            func = default
        return func(geometries, features)

    @staticmethod
    def get_translator_from_display_name(name):
        if name in Translator.translators:
            filename = Translator.translators[name]['filename']
            Translator.get_translator(filename)

    @staticmethod
    def get_translator(name):
        """
        Get a translator by name.  ultimately name is the basename without extension of a python module in sys.path
        The user can provide any name or path.  If the path exists, the directory is adde to sys.path, and the
        name is extracted.  If it is a simple name, then it is checked in
        1) the translations folder of the current directory,
        2) the translations folder of the script
        3) the cwd and the rest of sys.path.
        It is possible for a user to specify a translator that is a standard module, i.e. urllib, and if there is not
        a translator with that name in the translations folder, the standard module will be loaded as a tranlator.
        This will most likely be a harmless mistake as the translator will not have the required methods, and will do
        nothing.

        For the typical users, a list of the files in the translations folder of the script will be presented as choices


        :param name:
        :return:
        """
        # TODO Implement
        return name

    @staticmethod
    def get_well_known_display_names():
        return Translator.translators.keys()

    @staticmethod
    def isvalidshape(geomtype, display_name):
        return (display_name in Translator.translators and
                geomtype in Translator.translators[display_name]["geomtypes"])

    @staticmethod
    def get_display_names_for_shape(geomtype):
        return [name for name in Translator.translators if geomtype in Translator.translators[name]["geomtypes"]]

    @staticmethod
    def get_shapetypes_for_display_name(display_name):
        if display_name in Translator.translators:
            return Translator.translators[display_name]["geomtypes"]
        else:
            return []


# Read the names of well known translators when loading the module
set_translators()


def test():
    print sorted(Translator.get_well_known_display_names()) + ["Other"]
    print Translator.isvalidshape('Polygon', 'Buildings')
    for name in Translator.get_well_known_display_names():
        print name, Translator.get_shapetypes_for_display_name(name)
    for shapetype in ["Polygon", "Polyline", "Point"]:
        print shapetype, sorted(Translator.get_display_names_for_shape(shapetype)) + ["Other"]
