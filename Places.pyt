import arcpy
import arc2osmcore
import placescore
# import upload


class TranslatorUtils(object):
    # Display names for various translators
    translators = {
        'point': ["Points of Interest"],
        'line': ["Roads", "Trails"],
        'poly': ["Buildings", "Parking Lots"],
        'any': ["Generic", "Other"]
    }

    # File names for translators (when not the case insensitive display name)
    translator_names = {"Points of Interest": "poi",
                        "Parking Lots": "parkinglots"}

    all_translators = (translators['point'] + translators['line'] +
                       translators['poly'] + translators['any'])

    @staticmethod
    def get_translator(std_param, alt_param):
        translator = std_param.valueAsText
        if translator in TranslatorUtils.translator_names:
            translator = TranslatorUtils.translator_names[translator]
        if translator == "Other":
            translator = alt_param.valueAsText
        return translator

    @staticmethod
    def update_messages(fc_param, trans_param):
        if fc_param.value and trans_param.value:
            shapetype = arcpy.Describe(fc_param.value).shapeType
            translator = trans_param.value
            if ((shapetype == 'Polygon' and
                (translator in TranslatorUtils.translators['point'] or
                 translator in TranslatorUtils.translators['line'])) or
                (shapetype == 'Polyline' and
                (translator in TranslatorUtils.translators['point'] or
                 translator in TranslatorUtils.translators['poly'])) or
                (shapetype == 'Point' and
                (translator in TranslatorUtils.translators['poly'] or
                 translator in TranslatorUtils.translators['line']))):
                fc_param.setWarningMessage(
                    "Feature class shape does not match translator")
                trans_param.setWarningMessage(
                    "Translator does not match feature class shape.")

    @staticmethod
    def update_parameters(fc_param, trans_param, alt_param):
        alt_param.enabled = trans_param.value == 'Other'
        if fc_param.value:
            shapetype = arcpy.Describe(fc_param.value).shapeType
            if shapetype == 'Polygon':
                trans_param.filter.list = (
                    TranslatorUtils.translators['poly'] +
                    TranslatorUtils.translators['any'])
            if shapetype == 'Polyline':
                trans_param.filter.list = (
                    TranslatorUtils.translators['line'] +
                    TranslatorUtils.translators['any'])
            if shapetype == 'Point':
                trans_param.filter.list = (
                    TranslatorUtils.translators['point'] +
                    TranslatorUtils.translators['any'])

        fc_param.filter.list = ["Polygon", "Polyline", "Point"]
        if trans_param.value:
            if trans_param.value in TranslatorUtils.translators['poly']:
                fc_param.filter.list = ["Polygon"]
            if trans_param.value in TranslatorUtils.translators['line']:
                fc_param.filter.list = ["Polyline"]
            if trans_param.value in TranslatorUtils.translators['point']:
                fc_param.filter.list = ["Point"]


class Toolbox(object):
    """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
    def __init__(self):
        self.label = "Places Toolbox"
        self.alias = "Places"
        self.description = ("A collection of GIS tools for populating and "
                            "syncing Places with ArcGIS data (primarily data"
                            "in an EGIS data schema).")
        self.tools = [ValidateForPlaces,
                      SetupForPlaces,
                      CreatePlaceUpload,
                      PushUploadToPlaces,
                      IntegratePlacesIds,
                      SeedPlaces,
                      GetUpdatesFromPlaces,
                      PushUpdatesToPlaces]


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class ValidateForPlaces(object):
    def __init__(self):
        self.label = "1) Validate Data For Places"
        self.description = ("Checks if a feature class is suitable for "
                            "uploading to Places.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Feature Class",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        placescore.validate(parameters[0].valueAsText)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class SetupForPlaces(object):
    def __init__(self):
        self.label = "2) Setup Data For Places Syncing"
        self.description = ("Adds a PlacesID column and turns on archiving. "
                            "Feature class must be in a Geodatabase.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Feature Class",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        valid = placescore.validate(parameters[0].valueAsText, quiet=True)
        if valid == 'good':
            placescore.init4places(parameters[0].valueAsText)
        else:
            arcpy.AddWarning("Feature class is not suitable for Syncing.")
            # Run validation again to give the user the warnings.
            placescore.validate(parameters[0].valueAsText)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class CreatePlaceUpload(object):
    def __init__(self):
        self.label = "3) Creates a Places Upload File"
        self.description = ("Exports a feature class to a file "
                            "suitable for uploading to Places.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Input Features",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        output = arcpy.Parameter(
            name="output",
            displayName="Output File",
            direction="Input",
            datatype="GPString",
            parameterType="Required")

        translator = arcpy.Parameter(
            name="translator",
            displayName="Standard Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Required")
        translator.filter.list = TranslatorUtils.all_translators

        alt_translator = arcpy.Parameter(
            name="alt_translator",
            displayName="Alternate Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Required",
            enabled=False)

        parameters = [feature, output, translator, alt_translator]
        return parameters

    def updateParameters(self, parameters):
        TranslatorUtils.update_parameters(parameters[0], parameters[2],
                                          parameters[3])

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[2])

    def execute(self, parameters, messages):
        class Options:
            sourceFile = parameters[0].valueAsText
            outputFile = parameters[1].valueAsText
            translationMethod = TranslatorUtils.get_translator(parameters[2],
                                                               parameters[3])

        arc2osmcore.makeosmfile(Options)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class PushUploadToPlaces(object):
    def __init__(self):
        self.label = "4) Send Upload File to Places"
        self.description = ("Sends an OsmChange File to Places and creates "
                            "a CSV link table of Places Ids and EGIS Ids.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        upload = arcpy.Parameter(
            name="upload",
            displayName="OSM Change File",
            direction="Input",
            datatype="DEFile",
            parameterType="Required")
        upload.filter.list = ["osm"]

        response = arcpy.Parameter(
            name="response",
            displayName="Places ID File",
            direction="Input",
            datatype="GPString",
            parameterType="Required")

        parameters = [upload, response]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.AddWarning("Tool not Implemented.")


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class IntegratePlacesIds(object):
    def __init__(self):
        self.label = "5) Add Places Ids to EGIS"
        self.description = ("Populates the PlacesId in an EGIS dataset using "
                            "a CSV link table of Places Ids and EGIS Ids.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="EGIS Feature Class",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        idfile = arcpy.Parameter(
            name="idfile",
            displayName="Places ID File (CSV)",
            direction="Input",
            datatype="DEFile",
            parameterType="Required")
        idfile.filter.list = ["csv"]

        gisid = arcpy.Parameter(
            name="gisid",
            displayName="EGIS ID Field in EGIS",
            direction="Input",
            datatype="Field",
            parameterType="Required",
            category="Field Names",)
        gisid.parameterDependencies = [feature.name]
        gisid.value = 'GEOMETRYID'

        placesid = arcpy.Parameter(
            name="placesid",
            displayName="Places ID Field in EGIS",
            direction="Input",
            datatype="Field",
            parameterType="Required",
            category="Field Names",)
        placesid.parameterDependencies = [feature.name]
        placesid.value = 'PLACESID'
        placesid.filter.list = ['Text', 'Double', 'Long']

        gisidcsv = arcpy.Parameter(
            name="gisidcsv",
            displayName="EGIS ID Field in CSV",
            direction="Input",
            datatype="Field",
            parameterType="Required",
            category="Field Names",)
        gisidcsv.parameterDependencies = [idfile.name]
        gisidcsv.value = 'GEOMETRYID'

        placesidcsv = arcpy.Parameter(
            name="placesidcsv",
            displayName="Places ID Field in CSV",
            direction="Input",
            datatype="Field",
            parameterType="Required",
            category="Field Names",)
        placesidcsv.parameterDependencies = [idfile.name]
        placesidcsv.value = 'PLACESID'

        parameters = [feature, idfile, gisid, placesid, gisidcsv, placesidcsv]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        valid = placescore.validate(parameters[0].valueAsText, quiet=True)
        if valid == 'good':
            placescore.add_places_ids(parameters[0].valueAsText,
                                      parameters[1].valueAsText,
                                      parameters[2].valueAsText,
                                      parameters[3].valueAsText,
                                      parameters[4].valueAsText,
                                      parameters[5].valueAsText)
        else:
            arcpy.AddWarning("Feature class is not suitable for Integration.")
            # Run validation again to give the user the warnings.
            placescore.validate(parameters[0].valueAsText)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class SeedPlaces(object):
    def __init__(self):
        self.label = "Seed Places with EGIS data"
        self.description = ("Uploads a feature class to Places "
                            "and adds synchronization data to the "
                            "feature class")
        self.point_translators = ["Points of Interest"]
        self.line_translators = ["Roads", "Trails"]
        self.poly_translators = ["Buildings", "Parking Lots"]
        self.any_translators = ["Generic", "Other"]

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Input Feature",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")

        translator = arcpy.Parameter(
            name="translator",
            displayName="Standard Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Required")
        translator.filter.list = \
            self.point_translators + self.line_translators + \
            self.poly_translators + self.any_translators

        alt_translator = arcpy.Parameter(
            name="alt_translator",
            displayName="Alternate Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Required",
            enabled=False)

        parameters = [feature, translator, alt_translator]
        return parameters

    def updateParameters(self, parameters):
        TranslatorUtils.update_parameters(parameters[0], parameters[1],
                                          parameters[2])

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[1])

    def execute(self, parameters, messages):
        featureclass = parameters[0].valueAsText

        class Options:
            sourceFile = parameters[0].valueAsText
            outputFile = parameters[1].valueAsText
            translationMethod = TranslatorUtils.get_translator(parameters[1],
                                                               parameters[2])

        valid = placescore.validate(featureclass, quiet=True)
        if valid == 'good':
            if not placescore.init4places(featureclass):
                return
            # FIXME modify arc2osmcore to return the file contents
            changefile = arc2osmcore.makeosmfile(Options)
            if not changefile:
                return
            # FIXME get upload module
            csvfile = None
            # csvfile = upload(changefile)
            if not csvfile:
                return
            placescore.add_places_ids(featureclass, csvfile)
        else:
            arcpy.AddWarning("Feature class is not suitable for Places.")
            # Run validation again to give the user the warnings.
            valid = placescore.validate(featureclass)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class GetUpdatesFromPlaces(object):
    def __init__(self):
        self.label = "Get Updates from Places"
        self.description = ("... "
                            "...")

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Input Feature",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.AddWarning("Tool not Implemented.")


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class PushUpdatesToPlaces(object):
    def __init__(self):
        self.label = "Send Updates to Places"
        self.description = ("... "
                            "...")

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Input Feature",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.AddWarning("Tool not Implemented.")
