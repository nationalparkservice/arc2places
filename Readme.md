# arc2places

This project provides tools for uploading National Park Service GIS data
from ESRI data sources to the [NP Places system](http://www.nps.gov/npmap/tools/places/)
which is based on the OSM data model.

This kernel of this project was derived from Paul Norman's
[ogr2osm](https://github.com/pnorman/ogr2osm) tool which was derived from
the UVM tool of the same name.

Other documents that describe the
[workflows](https://github.com/nationalparkservice/arc2places/blob/master/Workflow.md)
supported by the
[Tools](https://github.com/nationalparkservice/arc2places/blob/master/Tools.md)
provided by this project

## Instalation
More details coming soon.  For now...

1. Clone or download this repository
2. Install Pip
    -- Windows: Download https://bootstrap.pypa.io/get-pip.py and run with python
    -- Others: is probably already install, if not use Google
3. Use Pip to install dependencies:
    ```pip install install requests_oauthlib
4. Create the secrets.py file. Currently, the tool only write to Places and relies on tokens that are
in the secrets.py file not included in the repo.
Contact [Regan](mailto:regan_sarwas@nps.gov) for assistance (NPS employees only)


## Places Toolbox (Places.pyt)
This is an ArcGIS Toolbox with tools for seeding GIS data to Places, and
planned tools for two way syncing between GIS data and Places.  This is the
primary interface for the typical ArcGIS user.

The toolbox provides both step by step tools, as well as a single *do it all in one step* tool.
During initial testing, the step by step tools are recommended.
It is also recomended that you test a full upload of your datasets against the test version of the Places database.

The ArcToolbox tools relies on the structure and files in the repo, so be sure to move it
as a unit.

The toolbox is primarily an ArcGIS interface to the same functionality
provided with the command line tools.  Additional information can be gleaned
by reading about the command line tools.

## Command line tools
There are command line versions of several of the tools in the toolbox suitable
batch processing or server side scripting on Windows.  There are versions of
some of the tools that do not require ArcGIS.  See [Command Line.md] for additional details.

## Translation Files
All tools rely on the [translation files](https://github.com/nationalparkservice/arc2places/tree/master/translations)
for the logic mapping ESRI data sources to Place tagging schemes.
The translation files are based on the Park Service EGIS Data Standards and the
[Places Tracing Guide](http://nationalparkservice.github.io/places-tracing-guide/).
They are fairly simple configuration files allowing them to be adapted to different
database schemas if necessary.
