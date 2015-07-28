__author__ = 'regan'

translator_names = []


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
    if name in translator_names:
        return Translator(name)
    return None

        translator = options.translationMethod
    defautltranslations = {
        'filterTags': lambda tags: tags,
        'filterFeature':
            lambda arcfeature, fieldnames, reproject: arcfeature,
        'filterFeaturePost':
            lambda feature, arcfeature, arcgeometry: feature,
        'preOutputTransform': lambda geometries, features: None
    }
    newtranslations = {}
    translationmodule = None

    if translator:
        # add dirs to path if necessary
        (root, ext) = os.path.splitext(translator)
        if os.path.exists(translator) and ext == '.py':
            # user supplied translation file directly
            sys.path.insert(0, os.path.dirname(root))
        else:
            # first check translations in the subdir translations of cwd
            sys.path.insert(0, os.path.join(os.getcwd(), "translations"))
            # then check subdir of script dir
            sys.path.insert(1, os.path.join(os.path.dirname(__file__),
                                            "translations"))
            # (the cwd will also be checked implicitly)

        # strip .py if present, as import wants just the module name
        if ext == '.py':
            translator = os.path.basename(root)

        try:
            translationmodule = __import__(translator, fromlist=[''])
        except ImportError:
            utils.die(
                u"Could not load translation method '{0:s}'. Translation "
                u"script must be in your current directory, or in the "
                u"'translations' subdirectory of your current or "
                u"arc2osmcore.py directory. The following directories have "
                u"been considered: {1:s}"
                .format(translator, str(sys.path)))
        except SyntaxError as e:
            utils.die(
                u"Syntax error in '{0:s}'."
                "Translation script is malformed:\n{1:s}"
                .format(translator, e))
        if options.verbose and translationmodule:
            utils.info(
                u"Successfully loaded '{0:s}' translation method ('{1:s}')."
                .format(translator,
                        os.path.realpath(translationmodule.__file__)))
    else:
        if options.verbose:
            utils.info("Using default translations")

    for k in defautltranslations:
        if hasattr(translationmodule, k) and getattr(translationmodule, k):
            newtranslations[k] = getattr(translationmodule, k)
            if options.verbose:
                utils.info("Using user " + k)
        else:
            newtranslations[k] = defautltranslations[k]
            if options.verbose and not translator:
                utils.info("Using default " + k)
    return newtranslations

import os

default_translations = {
        'filterTags': lambda tags: tags,
        'filterFeature':
            lambda arcfeature, fieldnames, reproject: arcfeature,
        'filterFeaturePost':
            lambda feature, arcfeature, arcgeometry: feature,
        'preOutputTransform': lambda geometries, features: None
    }

class Translator:
    def __init__(self, name, module):
        self.name = name
        self.path = os.path.realpath(module.__file__)

        for method in default_translations:
            if hasattr(translationmodule, k) and getattr(translationmodule, k):
            else:
                



# read the names when loading the module
