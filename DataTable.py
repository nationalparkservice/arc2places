__author__ = 'RESarwas'

import os


class DataTable:

    valid_field_types = ['TEXT', 'FLOAT', 'DOUBLE', 'SHORT', 'LONG', 'DATE' 'BLOB' 'RASTER' 'GUID']

    def __init__(self):
        self.fieldnames = None
        self.fieldtypes = None
        self.rows = []

    def export_csv(self, filepath, header=True):
        with open(filepath, 'wb') as f:
            self.export_csv_fd(f, header)

    def export_csv_fd(self, fd, header=True):
        import csv
        if header:
            fd.write(",".join(self.fieldnames) + '\n')
        csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in self.rows:
            csv_writer.writerow(row)

    def export_arcgis(self, workspace, table_name):
        try:
            import arcpy
        except ImportError:
            arcpy = None
        if arcpy is None:
            return
        arcpy.CreateTable_management(workspace, table_name)
        table_path = os.path.join(workspace, table_name)
        for fname, ftype in zip(self.fieldnames, self.fieldtypes):
            arcpy.AddField_management(table_path, fname, ftype)
        with arcpy.da.InsertCursor(table_path, self.fieldnames) as cursor:
            for row in self.rows:
                cursor.insertRow(row)


def test():
    data = DataTable()
    data.fieldnames = ['id', 'name']
    data.fieldtypes = ['LONG', 'TEXT']
    for row in [[1, 'a'], [2, 'b'], [3, 'c']]:
        data.rows.append(row)
    data.export_csv(r'c:\tmp\test.csv')
    data.export_arcgis(r'c:\tmp\test.gdb', 'simpletable2')
    sde = os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde")
    data.export_arcgis(sde, 'simpletable')


if __name__ == '__main__':
    test()
