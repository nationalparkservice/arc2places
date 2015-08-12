import os
import arcpy
import arc2osmcore
import placescore
import osm2places

# TODO: conditionally import OsmApiServer as it generates an ImportError if secret.py is missing,
# or sys.exit() if requests_oauthlib is missing which cause the toolbox to not load.

from OsmApiServer import OsmApiServer, Places
from Logger import ArcpyLogger
from Translator import Translator

places = Places()
places.logger = ArcpyLogger()
places.turn_verbose_on()
test_places = OsmApiServer('test')
test_places.logger = ArcpyLogger()
test_places.turn_verbose_on()


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
            arcpy.AddWarning(translator.error)
        else:
            arcpy.AddMessage(u"Successfully loaded '{0:s}' translation method ('{1:s}').".format(
                translator.name, translator.path))
            for function in translator.function_status:
                arcpy.AddMessage(u"Using {1:s} method for function '{0:s}'".format(
                    function, translator.function_status[function]))
        return translator

    @staticmethod
    def update_messages(fc_param, trans_param, alt_param):
        if fc_param.value and trans_param.value:
            shapetype = arcpy.Describe(fc_param.value).shapeType
            translator = trans_param.value
            if translator == "Other":
                if not alt_param.value:
                    alt_param.setErrorMessage("A translation is required.")
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
        TranslatorUtils.update_messages(parameters[0], parameters[1], parameters[2])

    def execute(self, parameters, messages):
        features = parameters[0].valueAsText
        translator = TranslatorUtils.get_translator(parameters[1], parameters[2])
        issues = placescore.valid4upload(features, places, translator)
        if issues:
            arcpy.AddWarning("Feature class is not suitable for uploading.")
            for issue in issues:
                arcpy.AddWarning(issue)
        else:
            issues = placescore.valid4sync(features, translator)
            if issues:
                arcpy.AddWarning("Feature class is not suitable for future Syncing.")
                for issue in issues:
                    arcpy.AddWarning(issue)
            else:
                arcpy.AddMessage("\nFeature class is suitable for uploading and syncing.\n")


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class EnableEditorTracking(object):
    def __init__(self):
        self.label = "2) Enable Editor Tracking"
        self.description = ("Enables editor tracking. "
                            "Feature class must be in a Geodatabase.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="Input Dataset",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        creator = arcpy.Parameter(
            name="creator",
            displayName="Creator Field",
            direction="Input",
            datatype="GPString",
            parameterType="Optional")
        creator.value = "CREATEUSER"

        create_date = arcpy.Parameter(
            name="create_date",
            displayName="Creation Date Field",
            direction="Input",
            datatype="GPString",
            parameterType="Optional")
        create_date.value = "CREATEDATE"

        editor = arcpy.Parameter(
            name="editor",
            displayName="Last Editor Field",
            direction="Input",
            datatype="GPString",
            parameterType="Optional")
        editor.value = "EDITUSER"

        edit_date = arcpy.Parameter(
            name="edit_date",
            displayName="Last Edit Date Field",
            direction="Input",
            datatype="GPString",
            parameterType="Optional")
        edit_date.value = "EDITDATE"

        addfields = arcpy.Parameter(
            name="addfields",
            displayName="Add fields if they don't exist",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required")
        addfields.value = False

        parameters = [feature, creator, create_date, editor, edit_date, addfields]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        features = parameters[0].valueAsText
        creator = parameters[1].valueAsText
        create_date = parameters[2].valueAsText
        editor = parameters[3].valueAsText
        edit_date = parameters[4].valueAsText
        add_fields = parameters[5].valueAsText
        if add_fields:
            add_fields_text = 'ADD_FIELDS'
        else:
            add_fields_text = 'NO_ADD_FIELDS'
        arcpy.EnableEditorTracking_management(features,
                                              creator_field=creator,
                                              creation_date_field=create_date,
                                              last_editor_field=editor,
                                              last_edit_date_field=edit_date,
                                              add_fields=add_fields_text)


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

        guid_field = arcpy.Parameter(
            name="guid_name",
            displayName="Name of Globally Unique Identifier Field",
            direction="Input",
            datatype="GPString",
            parameterType="Required")
        guid_field.value = "GEOMETRYID"

        parameters = [feature, guid_field]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        if parameters[0].value and parameters[1].value:
            if parameters[1].value in [f.name for f in arcpy.Describe(parameters[0].value).fields]:
                parameters[1].setErrorMessage("Field name already exists")
        return

    def execute(self, parameters, messages):
        features = parameters[0].valueAsText
        guid_field = parameters[1].valueAsText
        placescore.add_uniqueid_field(features, guid_field)


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

        folder = arcpy.Parameter(
            name="folder",
            displayName="Output Folder",
            direction="Input",
            datatype="DEFolder",
            parameterType="Required")

        output = arcpy.Parameter(
            name="output",
            displayName="File Name",
            direction="Input",
            datatype="GPString",
            parameterType="Required")

        parameters = [feature, translator, alt_translator, folder, output]
        return parameters

    def updateParameters(self, parameters):
        # update feature class <-> translator picklists
        TranslatorUtils.update_parameters(parameters[0], parameters[1], parameters[2])
        # create default output file name
        if parameters[0].value and not parameters[4].altered:
            basename = os.path.splitext(os.path.basename(parameters[0].valueAsText))[0]
            parameters[4].value = basename + os.path.extsep + 'osm'

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[1], parameters[2])
        if parameters[3].value and parameters[4].value:
            path = os.path.join(parameters[3].valueAsText, parameters[4].valueAsText)
            if os.path.exists(path):
                parameters[4].setErrorMessage("File {0:s} already exists.".format(path))

    def execute(self, parameters, messages):
        features = parameters[0].valueAsText
        translator = TranslatorUtils.get_translator(parameters[1], parameters[2])
        folder = parameters[3].valueAsText
        output_file = parameters[4].valueAsText
        options = arc2osmcore.DefaultOptions
        options.sourceFile = features
        options.outputFile = os.path.join(folder, output_file)
        options.translator = translator
        options.logger = ArcpyLogger()
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

        testing = arcpy.Parameter(
            name="testing",
            displayName="Upload to the testing version of Places",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required")
        testing.value = True

        parameters = [upload, workspace, log_table, testing]
        return parameters

    def updateParameters(self, parameters):
        # Default output workspace
        if parameters[0].value and not parameters[1].altered:
            dir_name = os.path.dirname(parameters[0].valueAsText)
            parameters[1].value = dir_name
        # Default table name
        if parameters[0].value and not parameters[2].altered:
            base_name = os.path.basename(parameters[0].valueAsText)
            base_name = os.path.splitext(base_name)[0]
            table_name = base_name + '_upload_log'
            if parameters[1].value:
                if arcpy.Describe(parameters[1].valueAsText).workspaceType == 'FileSystem':
                    table_name += '.csv'
            parameters[2].value = table_name
        # Ensure the table name is appropriate for the workspace
        if parameters[1].value and parameters[2].value:
            parameters[2].value = arcpy.ValidateTableName(parameters[2].valueAsText,
                                                          parameters[1].valueAsText)
            # undo conversion from '.csv' to '_csv'
            if (arcpy.Describe(parameters[1].valueAsText).workspaceType == 'FileSystem'
                    and parameters[2].valueAsText[-4:]) == '_csv':
                parameters[2].value = parameters[2].valueAsText[:-4] + '.csv'

    def updateMessages(self, parameters):
        if parameters[1].value and parameters[2].value:
            table_path = os.path.join(parameters[1].valueAsText, parameters[2].valueAsText)
            if arcpy.Exists(table_path):
                parameters[2].setErrorMessage("Output {0:s} already exists".format(table_path))

    def execute(self, parameters, messages):
        upload_path = parameters[0].valueAsText
        workspace = parameters[1].valueAsText
        table_name = parameters[2].valueAsText
        testing = parameters[3].value
        if testing:
            server = test_places
        else:
            server = places
        table_path = os.path.join(workspace, table_name)
        description = 'Upload of {0:s}.'.format(upload_path)
        table = None
        try:
            table = osm2places.upload_osm_file(upload_path, server, description)
        except osm2places.UploadError as e:
            arcpy.AddError(e)
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
                            "upload log table which links Places Ids to EGIS Ids.")
        self.category = "Seed Places Step by Step"

    def getParameterInfo(self):
        feature = arcpy.Parameter(
            name="feature",
            displayName="EGIS Feature Class",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required")
        feature.filter.list = ["Polygon", "Polyline", "Point"]

        table = arcpy.Parameter(
            name="table",
            displayName="Upload Log Table",
            direction="Input",
            datatype="DETable",
            parameterType="Required")

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
            displayName="EGIS ID Field in Upload Log",
            direction="Input",
            datatype="Field",
            parameterType="Required",
            category="Field Names",)
        gisidcsv.parameterDependencies = [table.name]
        gisidcsv.value = 'source_id'

        placesidcsv = arcpy.Parameter(
            name="placesidcsv",
            displayName="Places ID Field in Upload Log",
            direction="Input",
            datatype="Field",
            parameterType="Required",
            category="Field Names",)
        placesidcsv.parameterDependencies = [table.name]
        placesidcsv.value = 'places_id'

        parameters = [feature, table, gisid, placesid, gisidcsv, placesidcsv]
        return parameters

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        try:
            placescore.populate_related_field(parameters[0].valueAsText,
                                              parameters[1].valueAsText,
                                              parameters[2].valueAsText,
                                              parameters[3].valueAsText,
                                              parameters[4].valueAsText,
                                              parameters[5].valueAsText)
        except (TypeError, ValueError, arcpy.ExecuteError) as e:
            arcpy.AddError(str(e))


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

        testing = arcpy.Parameter(
            name="testing",
            displayName="Upload to the testing version of Places",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required")
        testing.value = True

        parameters = [feature, translator, alt_translator, workspace, log_table, ignore_sync_warnings, addIds, testing]
        return parameters

    def updateParameters(self, parameters):
        TranslatorUtils.update_parameters(parameters[0], parameters[1], parameters[2])
        # Default output workspace
        if parameters[0].value and not parameters[3].altered:
            dir_name = os.path.dirname(parameters[0].valueAsText)
            parameters[3].value = dir_name
        # Default table name
        if parameters[0].value and not parameters[4].altered:
            base_name = os.path.basename(parameters[0].valueAsText)
            table_name = base_name + '_upload_log'
            if parameters[3].value:
                if arcpy.Describe(parameters[3].valueAsText).workspaceType == 'FileSystem':
                    table_name += '.csv'
            parameters[4].value = table_name
        # Ensure the table name is appropriate for the workspace
        if parameters[3].value and parameters[4].value:
            parameters[4].value = arcpy.ValidateTableName(parameters[4].valueAsText,
                                                          parameters[3].valueAsText)
            # undo conversion from '.csv' to '_csv'
            if (arcpy.Describe(parameters[3].valueAsText).workspaceType == 'FileSystem'
                    and parameters[4].valueAsText[-4:]) == '_csv':
                parameters[4].value = parameters[4].valueAsText[:-4] + '.csv'

    def updateMessages(self, parameters):
        TranslatorUtils.update_messages(parameters[0], parameters[1], parameters[2])
        if parameters[3].value and parameters[4].value:
            table_path = os.path.join(parameters[3].valueAsText, parameters[4].valueAsText)
            if arcpy.Exists(table_path):
                parameters[4].setErrorMessage("Output {0:s} already exists".format(table_path))

    def execute(self, parameters, messages):
        featureclass = parameters[0].valueAsText
        translator = TranslatorUtils.get_translator(parameters[1], parameters[2])
        workspace = parameters[3].valueAsText
        table_name = parameters[4].valueAsText
        ignore_sync_warnings = parameters[5].value
        addIds = parameters[6].value
        testing = parameters[7].value
        if testing:
            server = test_places
        else:
            server = places
        if translator.translation_module is None:
            # Bad Translator.  Primary error was already printed
            arcpy.AddError("Aborting to avoid sending bad data to Places")
            return
        options = arc2osmcore.DefaultOptions
        options.sourceFile = featureclass
        options.outputFile = None
        options.translator = translator
        options.logger = ArcpyLogger()

        issues = placescore.valid4upload(featureclass, server, translator)
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
                    description = 'Initial upload of {0:s} translated with {1:s}'.format(featureclass, translator.name)
                    table = None
                    try:
                        table = osm2places.upload_osm_data(changefile, server, description)
                    except osm2places.UploadError as e:
                        arcpy.AddError(e)
                    if table:
                        table_path = os.path.join(workspace, table_name)
                        ext = os.path.splitext(table_name)[1].lower()
                        if arcpy.Describe(workspace).workspaceType == 'FileSystem' and ext in ['.csv', '.txt']:
                            table.export_csv(table_path)
                        else:
                            table.export_arcgis(workspace, table_name)
                        if addIds:
                            try:
                                placescore.populate_related_field(featureclass, table_path,
                                                                  primary_key_field_name='GEOMETRYID',
                                                                  destination_field_name='PLACESID',
                                                                  foreign_key_field_name='source_id',
                                                                  source_field_name='places_id')
                            except (TypeError, ValueError, arcpy.ExecuteError) as e:
                                arcpy.AddError(str(e))


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
