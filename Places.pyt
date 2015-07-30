import os
import arcpy
import arc2osmcore
import placescore
import osm2places
from OsmApiServer import Places
from Logger import ArcpyLogger
from Translator import Translator

places = Places()
places.logger = ArcpyLogger()
places.turn_verbose_on()


# TODO: make sure that any output file paths have invalid characters removed


class TranslatorUtils(object):
    """
    Provides coordination between translators and geometry type for all tools
    Also adds support for custom ("Other") translator (i.e. not in list of well known translators)
    """
    @staticmethod
    def get_display_names():
        return sorted(Translator.get_well_known_display_names()) + ["Other"]

    @staticmethod
    def get_translator(std_param, alt_param):
        std_translator = std_param.valueAsText
        alt_translator = alt_param.valueAsText
        if std_translator == "Other":
            translator = Translator.get_translator(alt_translator)
        else:
            translator = Translator.get_translator_from_display_name(std_translator)
        # Print diagnostics on the translator
        if translator.translation_module is None:
            arcpy.AddError(translator.error)
        else:
            arcpy.AddMessage(u"Successfully loaded '{0:s}' translation method ('{1:s}').".format(
                translator.name, translator.path))
            for function in translator.function_status:
                arcpy.AddMessage(u"Using {1:s} method for function '{0:s}'".format(
                    function, translator.function_status[function]))
        return translator

    @staticmethod
    def update_messages(fc_param, trans_param):
        if fc_param.value and trans_param.value:
            shapetype = arcpy.Describe(fc_param.value).shapeType
            translator = trans_param.value
            if translator == "Other":
                return  # no shape checking for Other
            if not Translator.isvalidshape(shapetype, translator):
                fc_param.setWarningMessage(
                    "Feature class shape does not match translator")
                trans_param.setWarningMessage(
                    "Translator does not match feature class shape.")

    @staticmethod
    def update_parameters(fc_param, trans_param, alt_param):
        if fc_param.value:
            shapetype = arcpy.Describe(fc_param.value).shapeType
            trans_param.filter.list = sorted(Translator.get_display_names_for_shape(shapetype)) + ["Other"]
        if trans_param.value:
            alt_param.enabled = trans_param.value == 'Other'
            if trans_param.value == 'Other':
                fc_param.filter.list = ["Polygon", "Polyline", "Point"]
            else:
                fc_param.filter.list = Translator.get_shapetypes_for_display_name(trans_param.value)


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
                      CreatePlacesUpload,
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

        translator = arcpy.Parameter(
            name="translator",
            displayName="Standard Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Optional")
        translator.filter.list = TranslatorUtils.get_display_names()

        alt_translator = arcpy.Parameter(
            name="alt_translator",
            displayName="Alternate Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Optional",
            enabled=False)

        parameters = [feature, translator, alt_translator]
        return parameters

    def updateParameters(self, parameters):
        TranslatorUtils.update_parameters(parameters[0], parameters[1], parameters[2])

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[1])

    def execute(self, parameters, messages):
        features = parameters[0].valueAsText
        translator = TranslatorUtils.get_translator(parameters[1], parameters[2])
        issues = placescore.valid4upload(features, places, translator)
        if issues:
            arcpy.AddWarning("Feature class is not suitable for Uploading.")
            for issue in issues:
                arcpy.AddWarning(issue)
        else:
            issues = placescore.valid4sync(features, translator)
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
        features = parameters[0].valueAsText
        arcpy.EnableEditorTracking_management(features,
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
class CreatePlacesUpload(object):
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
        translator.filter.list = TranslatorUtils.get_display_names()

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
        TranslatorUtils.update_parameters(parameters[0], parameters[2], parameters[3])

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[2])
        if parameters[1].value:
            path = parameters[1].valueAsText
            dir_path = os.path.dirname(path)
            if not os.path.exists(dir_path):
                parameters[1].AddError("Path {0:s} is not valid".format(dir_path))

    def execute(self, parameters, messages):
        features = parameters[0].valueAsText
        output_file = parameters[1].valueAsText
        translator = TranslatorUtils.get_translator(parameters[2], parameters[3])
        options = arc2osmcore.DefaultOptions
        options.sourceFile = features
        options.outputFile = output_file
        options.translator = translator
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

        workspace = arcpy.Parameter(
            name="workspace",
            displayName="Output Location",
            direction="Input",
            datatype="DEWorkspace",
            parameterType="Required")

        log_table = arcpy.Parameter(
            name="log_table",
            displayName="Upload Log Table",
            direction="Input",
            datatype="GPString",
            parameterType="Required")

        parameters = [upload, workspace, log_table]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        if parameters[1].value and parameters[2].value:
            table_path = os.path.join(parameters[1].valueAsText, parameters[2].valueAsText)
            if arcpy.Exists(table_path):
                parameters[2].setErrorMessage("Output {0:s} already exists".format(table_path))

    def execute(self, parameters, messages):
        upload_path = parameters[0].valueAsText
        workspace = parameters[1].valueAsText
        table_name = parameters[2].valueAsText
        table_path = os.path.join(workspace, table_name)
        error, table = osm2places.upload_osm_file(upload_path, places)
        if error:
            arcpy.AddError(error)
        if table:
            ext = os.path.splitext(table_name)[1].lower()
            if arcpy.Describe(workspace).workspaceType == 'FileSystem' and ext in ['.csv', '.txt']:
                table.export_csv(table_path)
            else:
                table.export_arcgis(workspace, table_name)


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
        translator.filter.list = TranslatorUtils.get_display_names()

        alt_translator = arcpy.Parameter(
            name="alt_translator",
            displayName="Alternate Translator",
            direction="Input",
            datatype="GPString",
            parameterType="Optional",
            enabled=False)

        workspace = arcpy.Parameter(
            name="workspace",
            displayName="Output Location",
            direction="Input",
            datatype="DEWorkspace",
            parameterType="Required")

        log_table = arcpy.Parameter(
            name="log_table",
            displayName="Upload Log Table",
            direction="Input",
            datatype="GPString",
            parameterType="Required")

        ignore_sync_warnings = arcpy.Parameter(
            name="ignore_sync_warnings",
            displayName="Ignore warnings about future syncing",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required")
        ignore_sync_warnings.value = False

        addIds = arcpy.Parameter(
            name="addIds",
            displayName="Add Places IDs to Input Feature",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required")
        addIds.value = False

        parameters = [feature, translator, alt_translator, workspace, log_table]
        return parameters

    def updateParameters(self, parameters):
        TranslatorUtils.update_parameters(parameters[0], parameters[1], parameters[2])

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[1])
        if parameters[3].value and parameters[4].value:
            table_path = os.path.join(parameters[3].valueAsText, parameters[3].valueAsText)
            if arcpy.Exists(table_path):
                parameters[2].setErrorMessage("Output {0:s} already exists".format(table_path))

    def execute(self, parameters, messages):
        featureclass = parameters[0].valueAsText
        translator = TranslatorUtils.get_translator(parameters[1], parameters[2])
        workspace = parameters[3].valueAsText
        table_name = parameters[4].valueAsText
        ignore_sync_warnings = parameters[4].value
        addIds = parameters[4].value
        if translator.translation_module is None:
            # Bad Translator.  Primary error was already printed
            arcpy.AddError("Aborting to avoid sending bad data to Places")
            return
        options = arc2osmcore.DefaultOptions
        options.sourceFile = featureclass
        options.outputFile = None
        options.translator = translator

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
                        table_path = os.path.join(workspace, table_name)
                        ext = os.path.splitext(table_name)[1].lower()
                        if arcpy.Describe(workspace).workspaceType == 'FileSystem' and ext in ['.csv', '.txt']:
                            table.export_csv(table_path)
                        else:
                            table.export_arcgis(workspace, table_name)
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
