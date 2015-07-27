__author__ = 'RESarwas'

import datetime
try:
    import arcpy
except ImportError:
    arcpy = None


class Logger:
    @staticmethod
    def debug(self, text):
        print('DEBUG', datetime.datetime.now(), text)

    @staticmethod
    def error(self, text):
        print('ERROR', text)

    @staticmethod
    def info(self, text):
        print('INFO', text)

    @staticmethod
    def warn(self, text):
        print('WARN', text)


class ArcpyLogger(Logger):
    @staticmethod
    def debug(self, text):
        if arcpy:
            arcpy.AddMessage(text)
        else:
            Logger.debug(self, text)

    @staticmethod
    def error(self, text):
        if arcpy:
            arcpy.AddError(text)
        else:
            Logger.info(self, text)

    @staticmethod
    def info(self, text):
        if arcpy:
            arcpy.AddMessage(text)
        else:
            Logger.info(self, text)

    @staticmethod
    def warn(self, text):
        if arcpy:
            arcpy.AddWarning(text)
        else:
            Logger.info(self, text)
