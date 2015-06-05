import arcpy
import arc2osmcore
import placescore


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
        self.category = "Step by Step"

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
        self.category = "Step by Step"

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
        self.category = "Step by Step"

        self.point_translators = ["Points of Interest"]
        self.line_translators = ["Roads", "Trails"]
        self.poly_translators = ["Buildings", "Parking Lots"]
        self.any_translators = ["Generic", "Other"]

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

        parameters = [feature, output, translator, alt_translator]
        return parameters

    def updateParameters(self, parameters):
        parameters[3].enabled = parameters[2].value == 'Other'
        if parameters[0].value:
            shapeType = arcpy.Describe(parameters[0].value).shapeType
            if shapeType == 'Polygon':
                parameters[2].filter.list = \
                    self.poly_translators + self.any_translators
            if shapeType == 'Polyline':
                parameters[2].filter.list = \
                    self.line_translators + self.any_translators
            if shapeType == 'Point':
                parameters[2].filter.list = \
                    self.point_translators + self.any_translators
        parameters[0].filter.list = ["Polygon", "Polyline", "Point"]
        if parameters[2].value:
            if parameters[2].value in self.poly_translators:
                parameters[0].filter.list = ["Polygon"]
            if parameters[2].value in self.line_translators:
                parameters[0].filter.list = ["Polyline"]
            if parameters[2].value in self.point_translators:
                parameters[0].filter.list = ["Point"]

    def updateMessages(self, parameters):
        if parameters[0].value and parameters[2].value:
            shapeType = arcpy.Describe(parameters[0].value).shapeType
            translator = parameters[2].value
            if ((shapeType == 'Polygon' and
                (translator in self.point_translators or
                 translator in self.line_translators)) or
                (shapeType == 'Polyline' and
                (translator in self.point_translators or
                 translator in self.poly_translators)) or
                (shapeType == 'Point' and
                (translator in self.poly_translators or
                 translator in self.line_translators))):
                parameters[0].setWarningMessage(
                    "Feature class shape does not match translator")
                parameters[2].setWarningMessage(
                    "Translator does not match feature class shape.")

    def execute(self, parameters, messages):
        translator = parameters[2].valueAsText
        translators = {"Points of Interest": "poi",
                       "Parking Lots": "parkinglots"}
        if translator in translators:
            translator = translators[translator]
        if translator == "Other":
            translator = parameters[3].valueAsText

        class Options:
            sourceFile = parameters[0].valueAsText
            outputFile = parameters[1].valueAsText
            translationMethod = translator

        arc2osmcore.makeosmfile(Options)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class PushUploadToPlaces(object):
    def __init__(self):
        self.label = "4) Send Upload File to Places"
        self.description = ("... "
                            "...")
        self.category = "Step by Step"

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
        self.description = ("... "
                            "...")
        self.category = "Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Input Features",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        idfile = arcpy.Parameter(
            name="idfile",
            displayName="Places ID File",
            direction="Input",
            datatype="DEFile",
            parameterType="Required")
        idfile.filter.list = ["csv"]

        parameters = [feature, idfile]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.AddWarning("Tool not Implemented.")


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class SeedPlaces(object):
    def __init__(self):
        self.label = "Seed Places with EGIS data"
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
