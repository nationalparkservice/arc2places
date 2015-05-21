This folder contains python translation files that work with ogr2osm and arc2osm
They translation files provided are appropriate for translating from the
National Park Service GIS data standards to the OSM format used by NP Places.
The translation files can easily be edited to translate non standard NPS GIS
datasets to the Places format.

There are five well known translation function names that will be used if
defined.  If they are defined, they must take the appropriate arguments, and
return the expected data type.

Translation Functions
=====================

filterLayer
-----------

Takes a ogr layer and returns the layer or None if the layer should be used
or ignored.  Ogr Layers are ways that OGR divides feature types in a data
source. For example, an AutoCAD datasource has different layers of data in it.
ArcGIS data sources generally do not have layers, so this feature is removed
from arc2osm.

filterTags
----------

This function is called for each feature in the dataset.
It takes a dictionary of attributes and returns a dictionary of tags.
The attribute keys are the column names in the dataset and the values
are the values of the feature converted to unicode strings by python.  For
example, a `NULL` in the database usually maps to `None` in python which will
be the string `u"None"`.
In Python dictionary keys are case sensitive (i.e. myColumn != MYCOLUMN).
`ogr2osm` provides the column name exactly as provided by the data source.
`arc2osm` first converts the column name to all uppercase.

filterFeature
-------------

Takes an ogr feature, a list of field names, and a boolean reproject flag. It returns
the feature to use or `None` if the feature is to be ignored.  For `arc2ogr`, this
is an arcgis feature.  This filter is done before any processing of the feature
is done.

filterFeaturePost
-----------------

Takes an internal feature, a list of field names, and a boolean reproject flag.
It returns a (modified) feature to use or `None` if the feature is to be ignored.
This filter is called after the geometry and tags have been parsed.  The feature
data type is defined in the `geom.py` file.  It has a geometry and a dictionary of tags.

preOutputTransform
------------------

This is called right before the list of features is written.  It takes a list
of features, and a list of geometries as defined in `geom.py`.  Nothing is returned,
but the input lists can be mutated as desired.


Using ogr2osm on the Mac
========================

1) Install FGDB API (optional)

This will allow GDAL to read esri file geodatabases (the common Park
Service GIS data format).  Browse to http://www.esri.com/apps/products/download/#File_Geodatabase_API_1.4
Select the version for os X 10.9 or greater use the clang version.  Use
the gcc version for older versions of Mac OSX.  You will need to log in to
esri's website with a esri global id (creating one is free) to finish the download.
After you unpack/unzip the fgdb download, copy (or link) the contents of the include folder
to /usr/local/include and the lib folder to /usr/local/lib (this is basically "installing"
the FileGDB API in your system)

2) Install homebrew (http://brew.sh/)

3) Install the gdal (http://www.gdal.org/) libraries

>>> brew install gdal --enable-unsupported

4) Install the python bindings for gdal

>>> sudo pip install GDAL

5) Install ogr2osm (https://github.com/pnorman/ogr2osm)

6) copy the translation files in this folder to the ogr2osm transations folder

7) Run ogr2osm

>>> python ogr2osm.py --help
>>> python ogr2osm.py /path/to/data.gdb/my_trails -o output.osm -t trails

Using ogr2osm on Windows
========================


Using arc2osm on the Mac
========================

Esri does not support ArcGIS on the Mac

Using arc2osm on Windows
========================

This requires ArcGIS to be installed on the windows computer.  It was tested
with ArcGIS 10.3 and python 2.7.5, however it should work with ArcGIS 10.1 sp1
and greater.  The python is suitable for 3.x and 2.7 so the scripts may work
with ArcGIS Pro, but this has not been tested.