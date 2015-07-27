__author__ = 'RESarwas'

import os

fieldnames = ['id', 'name']
valid_field_types = ['TEXT', 'FLOAT', 'DOUBLE', 'SHORT', 'LONG', 'DATE' 'BLOB' 'RASTER' 'GUID']
fieldtypes = ['LONG', 'TEXT']
rows = [[1, 'a'], [2, 'b'], [3, 'c']]


def export_csv(filepath, header=True):
    with open(filepath, 'wb') as f:
        export_csv_fd(f, header)


def export_csv_fd(fd, header=True):
    import csv
    if header:
        fd.write(",".join(fieldnames) + '\n')
    csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    for row in rows:
        csv_writer.writerow(row)


def export_arcgis(workspace, table_name):
    try:
        import arcpy
    except ImportError:
        arcpy = None
    if arcpy is None:
        return
    arcpy.CreateTable_management(workspace, table_name)
    table_path = os.path.join(workspace, table_name)
    for fname, ftype in zip(fieldnames, fieldtypes):
        arcpy.AddField_management(table_path, fname, ftype)
    with arcpy.da.InsertCursor(table_path, fieldnames) as cursor:
        for row in rows:
            cursor.insertRow(row)


def test_csv():
    export_csv(r'c:\tmp\test.csv')


def test_arcpy1():
    export_arcgis(r'c:\tmp\test.gdb', 'simpletable2')


def test_arcpy2():
    src = os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde")
    export_arcgis(src, 'simpletable')


if __name__ == '__main__':
    test_csv()
