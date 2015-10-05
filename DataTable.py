import os


def from_csv(filepath):
    import csv
    # Note: python 2.7 csv module does not support unicode; this CSV file should be all ASCII
    new_table = DataTable()
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            new_table.rows.append(row)
    new_table.fieldnames = reader.fieldnames
    return new_table


class DataTable:

    valid_field_types = ['TEXT', 'FLOAT', 'DOUBLE', 'SHORT', 'LONG', 'DATE' 'BLOB' 'RASTER' 'GUID']

    # Public - DataTables created/edited in make_upload_log() in osm2places; test() in self
    def __init__(self):
        self.fieldnames = None
        self.fieldtypes = None
        self.rows = []

    # Public - PushUploadToPlaces, SeedPlaces in arc2places.pyt, upload_osm_data() in osm2places; test() in self
    def export_csv(self, filepath, header=True, append=False):
        """
        Exports the data table to a CSV file.
        With Python2.7, the CSV module does not support unicode, so all data must be ASCII
        Header option is ignored, and set to False, when appending.
        When appending, caller is responsible for ensuring that data schema matches the exisiting file.
        May throw IOError exceptions opening/writing file.

        :param filepath: A path (string) to the new file.
        :param header: flag (bool) to turn on adding a header line at the start of the file.
        :param append: flag (bool) to add the data to the end of a file, otherwise an existing file is truncated.
        :return: Method has no return value.
        :rtype : None
        """
        if append:
            mode = 'a'
            header = False
        else:
            mode = 'w'
        # Note: python 2.7 csv module does not support unicode; this CSV file should be all ASCII
        with open(filepath, mode) as f:
            self.export_csv_fd(f, header)

    def export_csv_fd(self, fd, header=True):
        import csv
        if header:
            fd.write(",".join(self.fieldnames) + '\n')
        csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in self.rows:
            csv_writer.writerow(row)

    # Public - PushUploadToPlaces, SeedPlaces in arc2places.pyt; test() in self
    def export_arcgis(self, workspace, table_name, append=False):
        """
        Exports the data table to an ArcGIS dataset path.
        Does nothing if ArcGIS (arcpy) is not available.
        Will throw an exception if table exists and append == False
        Will throw an exception if append == True and table does not exist
        will throw an exception if append == True and schemas are different
        May throw other arcpy exceptions.

        :param workspace: A path (string) to an ArcGIS workspace
        :param table_name: The name (string) of the table to create/append in the ArcGIS workspace.
        :return: Method has no return value.
        :rtype : None
        """
        try:
            import arcpy
        except ImportError:
            arcpy = None
        if arcpy is None:
            return
        table_path = os.path.join(workspace, table_name)
        self.fieldnames = [arcpy.ValidateFieldName(f, workspace) for f in self.fieldnames]
        if not append:
            # will throw if table exists
            arcpy.CreateTable_management(workspace, table_name)
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
    data.export_csv(r'./testdata/simpletable.csv', append=True)
    data.export_arcgis('./testdata/test.gdb', 'simpletable')
    data.export_arcgis('./testdata/test.gdb', 'simpletable', append=True)
    sde = os.path.join("Database Connections", "akr_facility_on_inpakrovmais_as_gis.sde")
    data.export_arcgis(sde, 'simpletable')
    data.export_arcgis(sde, 'simpletable', append=True)
    new_data = from_csv(r'./testdata/simpletable.csv')
    print new_data.fieldnames
    for row in new_data.rows:
        print row


if __name__ == '__main__':
    test()
