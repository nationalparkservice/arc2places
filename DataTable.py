import os


class DataTable:

    valid_field_types = ['TEXT', 'FLOAT', 'DOUBLE', 'SHORT', 'LONG', 'DATE' 'BLOB' 'RASTER' 'GUID']

    def __init__(self):
        self.fieldnames = None
        self.fieldtypes = None
        self.rows = []

    # Public - PushUploadToPlaces, SeedPlaces in arc2places.pyt, upload_osm_data() in osm2places; test() in self
    def export_csv(self, filepath, header=True):
        """
        Exports the data table to a CSV file.
        May throw IOError exceptions opening/writing file.

        :param filepath: A path (string) to the new file.
        :param header: flag (bool) to turn on adding a header line at the start of the file.
        :return: Method has no return value.
        :rtype : None
        """
        # FIXME: This will kill an existing table.  In some cases we may want to append (check field match)
        # Note: python 2.7 csv module does not support unicode; this CSV file should be all ASCII
        with open(filepath, 'w') as f:
            self.export_csv_fd(f, header)

    def export_csv_fd(self, fd, header=True):
        import csv
        if header:
            fd.write(",".join(self.fieldnames) + '\n')
        csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in self.rows:
            csv_writer.writerow(row)

    # Public - PushUploadToPlaces, SeedPlaces in arc2places.pyt; test() in self
    def export_arcgis(self, workspace, table_name):
        """
        Exports the data table to an ArcGIS dataset path.
        Does nothing if ArcGIS (arcpy) is not available.
        May throw arcpy exceptions.

        :param workspace: A path (string) to an ArcGIS workspace
        :param table_name: The name (string) of the table to create in the ArcGIS workspace.
        :return: Method has no return value.
        :rtype : None
        """
        try:
            import arcpy
        except ImportError:
            arcpy = None
        if arcpy is None:
            return
        # FIXME: will fail if table exists.  In some cases we may want to append to existing (check field match)
        arcpy.CreateTable_management(workspace, table_name)
        table_path = os.path.join(workspace, table_name)
        self.fieldnames = [arcpy.ValidateFieldName(f, workspace) for f in self.fieldnames]
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
    data.export_csv(r'./testdata/simpletable.csv')
    data.export_arcgis('./testdata/test.gdb', 'simpletable')
    sde = os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde")
    data.export_arcgis(sde, 'simpletable')


if __name__ == '__main__':
    test()
