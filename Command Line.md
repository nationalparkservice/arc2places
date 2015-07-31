# Command line tools

**This document is out of date and needs major work.**

The tools in this project are written for NPS Employees, who are primary ArcGIS ArcToolbox users.
However command line tools are also useful, easier to test,
and potentially portable to other users.

Ultimately, I would like to create a modular library that is
* independent of, but relies on, either ArcGIS or [GDAL/OGR](http://www.gdal.org/) Drivers to read the datasets.
* works on all platfroms (Windows, Mac and Linux) python supports
* works with any OSM API Server.

Command line tools would be one interface to that library, and Command line tools would be another.


There are command line versions of several of the tools in the toolbox suitable
batch processing or server side scripting on Windows.  There are versions of
some of the tools that do not require ArcGIS

  * **arc2osm** - Create an upload file (in a standard OSM format)
     from an ESRI feature class (requires ArcGIS license).
  * **ogr2osm** - Create an upload file (in a standard OSM format) from an
     OGR dataset (could be ESRI feature class with suitable OGR drivers).
     Does not require an ArcGIS license and works on non-windows computers.
  * **osm2places** - Uploads an OsmChange file to Places, and creates a CSV link file
     with Places Ids matched to GEOMETRYID (configurable in translations).
     Does not require an ArcGIS licence but it does require active directory
     authentication to write to Places (details pending)
  * **placesids2arc** - Adds the Places Ids returned with osm2places to an
     ESRI feature class (currently requires an ArcGIS license)

##arc2osm and ogr2osm

###Create OSM upload file

To upload GIS features to Places you need to create an OSM upload file.
This can be done with ogr2osm or arc2osm on windows or Mac computers.
There are two upload file format available: [JOSM](http://wiki.openstreetmap.org/wiki/JOSM_file_format)
and [OsmChange](http://wiki.openstreetmap.org/wiki/OsmChange).

Currently, ogr2osm only creates the JOSM format, while arc2osm can create either.
See the [Upload to Places](https://github.com/regan-sarwas/arc2osm#upload-to-places)
for details on which format you should use.

All features in the JOSM and OsmChange files are considered new features to
be created in Places.

These tool can be slow for large dataset (based on the total number or vertices,
not features).  Consider breaking your data into smaller chunks if you have
problems.

####Supported ArcGIS geometries

* Points
* Polylines
* Polygons

Multipoints are possible with the command line tools (not the toolbox), however
they are treated as separate nodes (with the same tags).
No relationship is created because there is no [OSM multipoint relation](http://wiki.openstreetmap.org/wiki/Types_of_relation)
This causes a problem with syncing Places to GIS because there is not longer
a one-to-one map between the places id and nps:source_id, so **do not use multipoints**.
This shouldn't be a hardship as there probably aren't any multipoint feature classes in the NPS.
furthermore, even if we did create a new 'multipoint' type relation, neither
OSM nor ID would know how to deal with this.

Polylines with multiple paths are treated as separate ways (with the same tags).  No relationship is created.
This causes a problem with syncing Places to GIS because there is not longer
a one-to-one map between the places id and nps:source_id, so **do not use multipart polylines**.

Polygons are[ trouble](http://wiki.openstreetmap.org/wiki/The_Future_of_Areas#Way-based_Polygons)
The simple/common case of a single part polygon with one outer ring is modeled
as a closed way.  The building=* and the area=yes tags identify a closed way
as an area (polygon) feature.
If a single part polygon has multiple rings (i.e holes) it is created as
multipolygon relation with inner and outer members.  The element attributes
are on the relation.  A Multi-polygon is  treated as separate polygons, either
closed ways or relations.  Each polygon has the same tags. This causes a problem
with syncing Places to GIS because there is not longer a one-to-one map between
the places id and nps:source_id, so **do not use multipart poygons**.

####Issues
There are a few key fetures that are yet to be implemented
- [ ] merge multiple outer or outer/inner parts into one relationship for multi-polygons
- [ ] merge multi-part polylines into a single route type relation
- [ ] merge multi-part points into a single 'multipoint' type relation.
- [ ] Check Limits
OSM limits the number of nodes in a way to 2000, and the number of elements
in a changeset to 50000.  Places currently defaults to 50000 for both.
It is highly likely that there will be datasets with more than 50,000 vertices.
These will need to be split into multiple upload files.
It is also possible that there are ways with more than 50000 nodes. (ways this
big are also very hard for ID to deal with, so it may be that Places lowers
this limit closer to the OSM limit).  How should we deal with big ways?
1) Break the GIS features up into pieces (with unique ids) before exporting.
2) Create several ways from one GIS feature. This will break the one-to-one
referential integrity with th GIS.
3) Create several ways and join them in a route relation.  Put the tags on the
route.  Need to 'merge' the ways when syncing with GIS.


###Using arc2osm on Windows

This requires ArcGIS to be installed on the windows computer.  It was tested
with ArcGIS 10.3 and python 2.7.5, however it should work with ArcGIS 10.1 sp1
and greater.  The python is suitable for 3.x and 2.7 so the scripts may work
with ArcGIS Pro, but this has not been tested.

...[More to come]


###Using ogr2osm on Windows


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


###Using arc2osm on the Mac


Esri does not support ArcGIS on the Mac, so this option is not available.


###Using ogr2osm on the Mac


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

####TODO

- [ ] fork osm2ogr and add option to create OsmChange file
- [ ] fork osm2ogr and make the attribute names all upper case
- [ ] fork osm2ogr and fix multipoint creation


##Uploading to Places


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


###osm2places

This is a python script which takes an OsmChange file (and users credentials)
and uploads the changes to Places.  It uses the response from Places to create
a CSV file with the Places ID and GIS ID of each feature added to Places.

The GIS ID comes from the `nps:source_id` tag in the OsmChange file.  Any field in
the GIS data can be used as the source of the `nps:source_id` tag by using the
translation files.  The GIS ID field should be a unique key to the GIS data.
The translation files provided use the field `GEOMETRYID` (per the generic
GIS data standard)

Once a changeset is opened, this script will transform the OsmChange file to
use a valid changeset id. The input file is not changed, and the changeset id
is not saved.

```bash
python ogr2places.py /path/to/input.osm /path/to/output.csv
```


##Update ArcGIS data with Places Ids

...

###placesids2arc