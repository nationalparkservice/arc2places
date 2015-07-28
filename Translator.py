__author__ = 'regan'

import sys
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
            Translator.config = json.load(fp)
    except (IOError, ValueError):
        # If the file cannot be opened, IOError is raised
        # If the data being deserialized is not a valid JSON document, a ValueError will be raised.
        pass


class Translator:

    config = {}

    def __init__(self, name, module):
        self.name = name
        self.translation_module = module
        if getattr(module, '__file__', False):
            self.path = os.path.realpath(module.__file__)
        else:
            self.path = None

        self._filter_tags_function = self._get_filter_tags_function()
        self._filter_feature_function = self._get_filter_feature_function()
        self._filter_feature_post_function = self._get_filter_feature_post_function()
        self._transform_pre_output_function = self._get_transform_pre_output_function()

    def _get_filter_tags_function(self):
        default = lambda x: x
        func = get_function(self.translation_module, 'filter_tags')
        if func is None:
            func = get_function(self.translation_module, 'filterTags')
        if func is None:
            func = default
        return func

    def filter_tags(self, tags):
        return self._filter_tags_function(tags)

    def filter_feature(self, feature, fieldnames, reproject):
        return self._filter_feature_function(feature, fieldnames, reproject)

    def filter_feature_post(self, feature, arcfeature, arcgeometry):
        return self._filter_feature_post_function(feature, arcfeature, arcgeometry)

    def transform_pre_output(self, geometries, features):
        return self._transform_pre_output_function(geometries, features)

    def _get_filter_feature_function(self):
        default = lambda x, y, z: x
        func = get_function(self.translation_module, 'filter_feature')
        if func is None:
            func = get_function(self.translation_module, 'filterFeature')
        if func is None:
            func = default
        return func

    def _get_filter_feature_post_function(self):
        default = lambda x, y, z: x
        func = get_function(self.translation_module, 'filter_feature_post')
        if func is None:
            func = get_function(self.translation_module, 'filterFeaturePost')
        if func is None:
            func = default
        return func

    def _get_transform_pre_output_function(self):
        default = lambda x, y: None
        func = get_function(self.translation_module, 'transform_pre_output')
        if func is None:
            func = get_function(self.translation_module, 'preOutputTransform')
        if func is None:
            func = default
        return func

    @staticmethod
    def get_translator_from_display_name(name):
        if name in Translator.config:
            filename = Translator.config[name]['filename']
            Translator.get_translator(filename)

    @staticmethod
    def get_translator(filename):
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

        :param filename: a basename or full path of a python module
        :return: an instance of the Translator class
        """
        if not filename:
            error = 'No name provided, using the default (identity) translators'
            return Translator(filename, None)

        # add dirs to sys.path if necessary
        (root, ext) = os.path.splitext(filename)
        if os.path.exists(filename) and ext == '.py':
            # user supplied translation file directly
            path = os.path.dirname(root)
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
        else:
            # first check translations in the subdir translations of cwd
            path = os.path.join(os.getcwd(), "translations")
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
            # then check subdir of script dir
            path = os.path.join(os.path.dirname(__file__), "translations")
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(1, path)
            # (the cwd will also be checked implicitly)

        # strip .py if present, as import wants just the module name
        if ext == '.py':
            filename = os.path.basename(root)

        translationmodule = None
        try:
            translationmodule = __import__(filename, fromlist=[''])
        except ImportError:
            error = (
                u"Could not load translation method '{0:s}'. Translation "
                u"script must be in your current directory, or in the "
                u"'translations' subdirectory of your current or "
                u"arc2osmcore.py directory. The following directories have "
                u"been considered: {1:s}"
                .format(filename, str(sys.path)))
        except SyntaxError as e:
            error = (
                u"Syntax error in '{0:s}'."
                "Translation script is malformed:\n{1:s}"
                .format(filename, e))
        msg = u"Successfully loaded '{0:s}' translation method ('{1:s}')."\
            .format(filename, os.path.realpath(translationmodule.__file__))

        return Translator(filename, translationmodule)

    @staticmethod
    def get_well_known_display_names():
        return Translator.config.keys()

    @staticmethod
    def isvalidshape(geomtype, display_name):
        return (display_name in Translator.config and
                geomtype in Translator.config[display_name]["geomtypes"])

    @staticmethod
    def get_display_names_for_shape(geomtype):
        return [name for name in Translator.config if geomtype in Translator.config[name]["geomtypes"]]

    @staticmethod
    def get_shapetypes_for_display_name(display_name):
        if display_name in Translator.config:
            return Translator.config[display_name]["geomtypes"]
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
