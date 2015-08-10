# arc2places

This project provides tools for uploading National Park Service GIS data
from ESRI data sources to the [NP Places system](http://www.nps.gov/npmap/tools/places/)
which is based on the OSM data model.
It was built to support the [centennial data call](http://insidemaps.nps.gov/places/data-call/)(NPS-only)

This kernel of this project was derived from Paul Norman's
[ogr2osm](https://github.com/pnorman/ogr2osm) tool which was derived from
the UVM tool of the same name.

Other documents describe the
[workflow](https://github.com/nationalparkservice/arc2places/blob/master/workflow.md)
supported by the
[tools](https://github.com/nationalparkservice/arc2places/blob/master/Tools.md)
in this project.

## Installation

National Park Service employees using ArcGIS Desktop can find installation help
at http://akrgis.nps.gov/apps/arc2places/ (NPS-only)

Others can try the following:

1. Clone or download this repository
2. Install Pip

    * Windows: Download https://bootstrap.pypa.io/get-pip.py and run with python.
    * Others: it is probably already install, if not use Google.

3. Use Pip to install dependencies:

    * ```pip install requests_oauthlib```

4. Create the secrets.py file. Currently, the tool only writes to the NPS internal Places database
and relies on tokens that are in the secrets.py file not included in the repo.
Contact [Regan](mailto:regan_sarwas@nps.gov) for assistance (NPS-only)


## Places Toolbox
**Places.pyt** is an ArcGIS Python Toolbox with tools for seeding ArcGIS data to Places.
It includes place holders for planned tools for two way syncing between ArcGIS data and Places.
This is the primary interface for the typical NPS ArcGIS user.

The toolbox provides both step by step tools, as well as a *do it all in one step* tool.
The step by step tools are recommended until you are familiar with how the tool works and the suitability of your datasets.
You should also test your datasets against the test version of the Places database before doing your production upload.
Testing the toolbox is easier if you turn off *Background Processing* in the Geoprocessing Options.

The ArcToolbox tools relies on the structure and files in the repo, so be sure to move it
as a unit.

The toolbox is primarily an ArcGIS interface to the same functionality
provided with the command line tools.  Additional information can be gleaned
by reading about the command line tools.

## Command line tools
There are command line versions of several of the tools in the toolbox.
These are suitable for batch processing or server side scripting on Windows.
There are versions of some of the tools that do not require ArcGIS or Windows.
See [Command Line.md](https://github.com/nationalparkservice/arc2places/blob/master/Command%20Line.md)
for additional details.

## Translation Files
All tools rely on the [translation files](https://github.com/nationalparkservice/arc2places/tree/master/translations)
for the logic to convert the fields/values in ESRI data sources to the Places tagging schemes.
The translation files are based on the Park Service EGIS Data Standards and the
[Places Tracing Guide](http://www.nps.gov/npmap/tools/places/tracing-guide/).
They are fairly simple configuration files allowing them to be adapted to different
database schemas if necessary.

## Building
To build the installation bundle for the website:
1 get latest version of 'getpip.py' from https://bootstrap.pypa.io/get-pip.py
2 get latest version of arc2places from https://github.com/nationalparkservice/arc2places/tree/master
3 get latest version of secrets.py from regan_sarwas@nps.gov
4 Package into a zip file called arc2places.zip:
  * get-pip.py
  * secrets.py
  * arc2places.pyt
  * *.py
  * *.pyt.xml
  * translations folder

