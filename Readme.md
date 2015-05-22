arc2osm
=======

This project provides tools for uploading National Park Service GIS data
from ESRI data sources to the [NP Places system](https://github.com/nationalparkservice/places-api)
which is based on the OSM data model.

This work was derived from Paul Norman's [ogr2osm](https://github.com/pnorman/ogr2osm) tool which was derived from
the UVM tool of the same name.


Create OSM upload file
======================

To upload GIS features to Places you need to create an OSM upload file.
This can be done with ogr2osm or arc2osm on windows or Mac computers.
There are two upload file format available: [JOSM](http://wiki.openstreetmap.org/wiki/JOSM_file_format)
and [OsmChange](http://wiki.openstreetmap.org/wiki/OsmChange).

Currently, ogr2osm only creates the JOSM format, while arc2osm can create either.
See the [Upload to Places](https://github.com/regan-sarwas/arc2osm/tree/master/#upload-to-places)
for details on which format you should use.

All features in the JOSM and OsmChange files are considered new features to
be created in Places.


Using arc2osm on Windows
------------------------

This requires ArcGIS to be installed on the windows computer.  It was tested
with ArcGIS 10.3 and python 2.7.5, however it should work with ArcGIS 10.1 sp1
and greater.  The python is suitable for 3.x and 2.7 so the scripts may work
with ArcGIS Pro, but this has not been tested.

...[More to come]


Using ogr2osm on Windows
------------------------

For Windows users with ArcGIS installed, I recommend using arc2osm.
The following has not been tested, so proceed at your own risk.

1) Install FGDB API (optional)

This will allow GDAL to use esri file geodatabases (the common Park
Service GIS data format). For read only FGDB access the drivers are provided
with GDAL.  If you need to write to FGDBs you will need to install the drivers
provided by esri. Browse to http://www.esri.com/apps/products/download/#File_Geodatabase_API_1.4
Select the version Visual Studio that you use (if you do not use Visual Studio,
then any version will work)

2) Install GDAL with Python Bindings

There are many options - see http://gis.stackexchange.com/questions/2276/how-to-install-gdal-with-python-on-windows
for details.


Using arc2osm on the Mac
------------------------

Esri does not support ArcGIS on the Mac, so this option is not available.


Using ogr2osm on the Mac
------------------------

1) Install FGDB API (optional)

This will allow GDAL to read/write esri file geodatabases (the common Park
Service GIS data format).  Browse to http://www.esri.com/apps/products/download/#File_Geodatabase_API_1.4
Select the version for os X 10.9 or greater use the clang version.  Use
the gcc version for older versions of Mac OSX.  You will need to log in to
esri's website with a esri global id (creating one is free) to finish the download.
After you unpack/unzip the fgdb download, copy (or link) the contents of the include folder
to /usr/local/include and the lib folder to /usr/local/lib (this is basically "installing"
the FileGDB API in your system)

2) Install homebrew (http://brew.sh/)

3) Install the gdal (http://www.gdal.org/) libraries

```bash
 brew install gdal --enable-unsupported
```

4) Install the python bindings for gdal

```bash
sudo pip install GDAL
```

5) Install ogr2osm (https://github.com/pnorman/ogr2osm)

6) copy the translation files in this folder to the ogr2osm transations folder

7) Run ogr2osm

```bash
python ogr2osm.py --help
python ogr2osm.py /path/to/data.gdb/my_trails -o output.osm -t trails
```

###TODO

- [ ] fork osm2ogr and add option to create OsmChange file


Upload to Places
================

The JOSM format can be uploaded to Places with the [JOSM editor](http://wiki.openstreetmap.org/wiki/JOSM),
or with [osmosis](http://wiki.openstreetmap.org/wiki/Osmosis) if you have direct access to the Places database

The OsmChange format can be uploaded to Places with the
[upload changeset](http://wiki.openstreetmap.org/wiki/API_v0.6#Diff_upload:_POST_.2Fapi.2F0.6.2Fchangeset.2F.23id.2Fupload)
command in the OSM 0.6 API.

The OsmChange file created by arc2osm uses a sentinal of `changeset="-1"` to
represent the unknown changeset id.  The OsmChange file must be edited to
replace the sentinal with a valid changeset id once a changeset is opened with
the OSM API.  A valid authorization token is required to open create a changeset.

The benefit of using the API to upload an OsmChange file is that the API returns
the OSM (Places) IDs of created features.  This allows the creation of a link
file which can be used for syncing GIS data with Places data.

osm2places
----------

This is a python script which takes an OsmChange file (and users credentials)
and uploads the changes to Places.  It uses the response from Places to create
a CSV file with the Places ID and GIS ID of each feature added to Places. The
GIS ID comes from the `nps:source_id` tag in the OsmChange file.  Any field in
the GIS data can be used as the source of the `nps:source_id` tag by using the
translation files.  The GIS ID field should be a unique key to the GIS data.
The translation files provided use the field `GEOMETRYID` (per the generic
GIS data standard)


Update ArcGIS data with Places Ids
==================================

...
