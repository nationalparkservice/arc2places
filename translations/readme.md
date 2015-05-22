Ogr2osm Translation Files
=========================

This folder contains python translation files that work with ogr2osm and arc2osm.
The translation files provided are appropriate for translating from the
National Park Service GIS data standards to the OSM format used by NP Places.
The translation files can easily be copied and edited to translate non-standard
NPS GIS datasets to the Places format.  They will also work as-is with any dataset,
however unrecognized field names will be ignore, so the resulting feature
in Places may not get any of your attributes.

If you use the appropriate translation file you should get a reasonable
default places feature provided you have a field called `NAME` (or the equivalent
data standard field name) in your GIS dataset.

The translation files can declare one or more of the five well known translation functions.
If a well known function is defined it will be used as decribed below.
The functions must take the appropriate arguments, and return the expected data type.


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

Takes an ogr feature, a list of field names, and a boolean reproject flag.
It returns the feature to use or `None` if the feature is to be ignored.
For `arc2ogr`, the feature is an arcGIS cursor row (a tuple - the order of values
in the tuple matches the order of fields in field names with the geometry as
the first value).  This filter is done before any processing of the feature
is done.

filterFeaturePost
-----------------

Takes a feature, a list of field names, and a boolean reproject flag.
It returns a (modified) feature to use or `None` if the feature is to be ignored.
This filter is called once for each feature after the geometry and tags have
been parsed.  The feature data type is defined in the `geom.py` file.
It has a geometry and a dictionary of tags.

preOutputTransform
------------------

This is called right before the list of features is written.  It takes a list
of features and a list of geometries as defined in `geom.py`.  Nothing is returned,
but the input lists can be mutated as desired.
