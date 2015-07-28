__author__ = 'regan'

import sys
import os
import json
import inspect


def get_function(module, name, arg_count):
    try:
        func = getattr(module, name)
        getattr(func, '__call__')
    except AttributeError:
        func = None
    if func and len(inspect.getargspec(func).args) != arg_count:
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

    def __init__(self, name, module, error=None):
        """
        Create a new Translator, not not call directly user Translator.get_translator()
        """
        self.name = name
        self.translation_module = module
        if getattr(module, '__file__', False):
            self.path = os.path.realpath(module.__file__)
        else:
            self.path = None
        self.error = error
        self.function_status = {}

        # Function in the module with the correct name and number of arguments are
        # assigned to the predefined methods of the translator object.
        self._filter_tags_function = self._get_filter_tags_function()
        self._filter_feature_function = self._get_filter_feature_function()
        self._filter_feature_post_function = self._get_filter_feature_post_function()
        self._transform_pre_output_function = self._get_transform_pre_output_function()

    def filter_tags(self, tags):
        return self._filter_tags_function(tags)

    def filter_feature(self, feature, fieldnames, reproject):
        return self._filter_feature_function(feature, fieldnames, reproject)

    def filter_feature_post(self, feature, arcfeature, arcgeometry):
        return self._filter_feature_post_function(feature, arcfeature, arcgeometry)

    def transform_pre_output(self, geometries, features):
        return self._transform_pre_output_function(geometries, features)

    def _get_filter_tags_function(self):
        default = lambda x: x
        self.function_status['filter_tags'] = 'Custom'
        func = get_function(self.translation_module, 'filter_tags', 1)
        if func is None:
            func = get_function(self.translation_module, 'filterTags', 1)
        if func is None:
            func = default
            self.function_status['filter_tags'] = 'Default'
        return func

    def _get_filter_feature_function(self):
        default = lambda x, y, z: x
        self.function_status['filter_feature'] = 'Custom'
        func = get_function(self.translation_module, 'filter_feature', 3)
        if func is None:
            func = get_function(self.translation_module, 'filterFeature', 3)
        if func is None:
            func = default
            self.function_status['filter_feature'] = 'Default'
        return func

    def _get_filter_feature_post_function(self):
        default = lambda x, y, z: x
        self.function_status['filter_feature_post'] = 'Custom'
        func = get_function(self.translation_module, 'filter_feature_post', 3)
        if func is None:
            func = get_function(self.translation_module, 'filterFeaturePost', 3)
        if func is None:
            func = default
            self.function_status['filter_feature_post'] = 'Default'
        return func

    def _get_transform_pre_output_function(self):
        default = lambda x, y: None
        self.function_status['transform_pre_output'] = 'Custom'
        func = get_function(self.translation_module, 'transform_pre_output', 2)
        if func is None:
            func = get_function(self.translation_module, 'preOutputTransform', 2)
        if func is None:
            func = default
            self.function_status['transform_pre_output'] = 'Default'
        return func

    @staticmethod
    def get_translator_from_display_name(name):
        if name in Translator.config:
            filename = Translator.config[name]['filename']
            return Translator.get_translator(filename)
        else:
            return Translator.get_translator(None)

    @staticmethod
    def get_translator(filename):
        """
        Get a translation module by name.

        The user can provide a name or path.
        if a python file exists at the path, then it is loaded as a module.
        If a name is provided, then the following folders are searched for name[.py]
        1) the translations folder of the current directory,
        2) the translations folder of the script's directory
        3) the cwd and the rest of sys.path.

        :param filename: a basename or full path of a python module
        :return: an instance of the Translator class
        """
        if not filename:
            error = 'No name provided, using the default (identity) translators'
            return Translator(filename, None, error)

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
        error = None
        try:
            translationmodule = __import__(filename, fromlist=[''])
        except ImportError:
            error = (
                u"Could not load translation method '{0:s}'. Translation "
                u"script must be in your current directory, or in the "
                u"'translations' subdirectory of your current or "
                u"script directory. The following directories have "
                u"been considered: {1:s}"
                .format(filename, str(sys.path)))
        except SyntaxError as e:
            error = (
                u"Syntax error in '{0:s}'."
                u"Translation script is malformed:\n{1:s}"
                .format(filename, e))

        return Translator(filename, translationmodule, error)

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


def test1():
    print sorted(Translator.get_well_known_display_names()) + ["Other"]
    print Translator.isvalidshape('Polygon', 'Buildings')
    for name in Translator.get_well_known_display_names():
        print name, Translator.get_shapetypes_for_display_name(name)
    for shapetype in ["Polygon", "Polyline", "Point"]:
        print shapetype, sorted(Translator.get_display_names_for_shape(shapetype)) + ["Other"]


def test2():
    for translator in [Translator.get_translator('poi'),
                       Translator.get_translator('poix'),
                       Translator.get_translator('poix'),
                       Translator.get_translator_from_display_name('Parking Lots'),
                       Translator.get_translator(None),
                       Translator.get_translator(''),
                       Translator.get_translator(r'C:\Users\resarwas\Documents\GitHub\arc2places\geom.py')]:
        print '\nTranslator', translator.name, '\n'
        if translator.translation_module is None:
            print 'Error:', translator.error
        else:
            print u"Successfully loaded '{0:s}' translation method ('{1:s}').".format(
                str(translator.name), str(translator.path))
            print translator.function_status
        print translator.filter_tags({'ALTNAME': 'Regan'})
        print translator.filter_tags({'POITYPE': 'Lake'})

if __name__ == '__main__':
    test1()
    test2()
