from __future__ import print_function
import datetime


class Logger:
    def debug(self, text):
        print('DEBUG', datetime.datetime.now(), text)

    def error(self, text):
        print('ERROR', text)

    def info(self, text):
        print('INFO', text)

    def warn(self, text):
        print('WARN', text)


class ArcpyLogger(Logger):
    def __init__(self):
        try:
            self.arcpy = __import__('arcpy')
        except ImportError:
            self.arcpy = None

    def debug(self, text):
        if self.arcpy:
            self.arcpy.AddMessage(text)
        else:
            Logger.debug(self, text)

    @staticmethod
    def error(self, text):
        if self.arcpy:
            self.arcpy.AddError(text)
        else:
            Logger.info(self, text)

    @staticmethod
    def info(self, text):
        if self.arcpy:
            self.arcpy.AddMessage(text)
        else:
            Logger.info(self, text)

    @staticmethod
    def warn(self, text):
        if self.arcpy:
            self.arcpy.AddWarning(text)
        else:
            Logger.info(self, text)
