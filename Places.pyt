import arcpy
import arc2osmcore
import placescore
import osm2places

# TODO: configure the places server
places = placescore.Places('http://url.to.server')


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
                      EnableEditorTracking,
                      AddUniqueId,
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
                            "uploading and syncing to Places.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Feature Class",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        # TODO - Add optional translator parameter; used to filter features

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        translator = None  # parameters[1].valueAsText
        issues = placescore.valid4upload(parameters[0].valueAsText, places, translator)
        if issues:
            arcpy.AddWarning("Feature class is not suitable for Uploading.")
            for issue in issues:
                arcpy.AddWarning(issue)
        else:
            issues = placescore.valid4sync(parameters[0].valueAsText, translator)
            if issues:
                arcpy.AddWarning("Feature class is not suitable for future Syncing.")
                for issue in issues:
                    arcpy.AddWarning(issue)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class EnableEditorTracking(object):
    def __init__(self):
        self.label = "2) Enable Editor Tracking"
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

        # TODO - Add parameters for call to arcpy.EnableEditorTracking_management()

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.EnableEditorTracking_management(parameters[0].valueAsText,
                                              last_edit_date_field='EDITDATE', add_fields='ADDFIELDS')


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class AddUniqueId(object):
    def __init__(self):
        self.label = "3) Add and populate a unique feature id for syncing"
        self.description = "Adds and populates a unique feature id (GUID) for syncing. "
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Feature Class",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        # TODO - add column name option, default to GEOMETRYID

        parameters = [feature]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        # TODO: Implement
        arcpy.AddWarning("Tool not Implemented.")


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class CreatePlaceUpload(object):
    def __init__(self):
        self.label = "4) Creates a Places Upload File"
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
        options = arc2osmcore.DefaultOptions
        options.sourceFile = parameters[0].valueAsText
        options.outputFile = parameters[1].valueAsText
        options.translationMethod = TranslatorUtils.get_translator(
            parameters[2], parameters[3])
        arc2osmcore.makeosmfile(options)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class PushUploadToPlaces(object):
    def __init__(self):
        self.label = "5) Send Upload File to Places"
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
            displayName="Upload Log Table",
            direction="Input",
            datatype="GPString",
            parameterType="Required")

        # TODO: need to add workspace parameter (selection)

        parameters = [upload, response]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        # TODO make sure table does not exist in workspace
        return

    def execute(self, parameters, messages):
        upload_path = parameters[0].valueAsText
        response_path = parameters[1].valueAsText
        error, table = osm2places.upload_osm_file(upload_path, places)
        if error:
            arcpy.AddError(error)
        if table:
            # TODO: save the table to response_path
            pass


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class IntegratePlacesIds(object):
    def __init__(self):
        self.label = "6) Add Places Ids to EGIS"
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
        placescore.add_places_ids(parameters[0].valueAsText,
                                  parameters[1].valueAsText,
                                  parameters[2].valueAsText,
                                  parameters[3].valueAsText,
                                  parameters[4].valueAsText,
                                  parameters[5].valueAsText)


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
            parameterType="Optional",
            enabled=False)

        # FIXME - osm2places returns a upload log table, need option for save this table
        # TODO - Add option to upload without future syncing (ignore sync warnings)
        # TODO - Add option to add Places IDs to feature class.

        parameters = [feature, translator, alt_translator]
        return parameters

    def updateParameters(self, parameters):
        TranslatorUtils.update_parameters(parameters[0], parameters[1],
                                          parameters[2])

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[1])

    def execute(self, parameters, messages):
        featureclass = parameters[0].valueAsText
        options = arc2osmcore.DefaultOptions
        options.sourceFile = featureclass
        options.outputFile = None
        options.translationMethod = TranslatorUtils.get_translator(
            parameters[1], parameters[2])
        # TODO - Get a translator object
        translator = None
        # TODO - Get option from parameters
        ignore_sync_warnings = False
        #  TODO - Get option from parameters
        addIds = False

        issues = placescore.valid4upload(featureclass, places, translator)
        if issues:
            arcpy.AddWarning("Feature class is not suitable for Uploading.")
            for issue in issues:
                arcpy.AddWarning(issue)
        else:
            sync_issues = placescore.valid4sync(featureclass, translator)
            if sync_issues:
                arcpy.AddWarning("Feature class is not suitable for future Syncing.")
                for issue in sync_issues:
                    arcpy.AddWarning(issue)
            if not sync_issues or ignore_sync_warnings:
                error, changefile = arc2osmcore.makeosmfile(options)
                if error:
                    arcpy.AddError(error)
                else:
                    error, table = osm2places.upload_osm_data(changefile, places)
                    if error:
                        arcpy.AddError(error)
                    if table:
                        # TODO save the table
                        if addIds:
                            placescore.add_places_ids(featureclass, table)


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class GetUpdatesFromPlaces(object):
    def __init__(self):
        self.label = "Get Updates from Places"
        self.description = ("Query the Places system for new edits "
                            "and create a feature class or version "
                            "for reconciliation with master version.")

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
        # FIXME: Implement
        arcpy.AddWarning("Tool not Implemented.")


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class PushUpdatesToPlaces(object):
    def __init__(self):
        self.label = "Send Updates to Places"
        self.description = ("Find changes to the dataset used to seed "
                            "and push those changes to Places")

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
        # FIXME: Implement
        arcpy.AddWarning("Tool not Implemented.")
