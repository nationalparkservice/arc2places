#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et
import optparse
import os
import sys
import datetime
from OsmApiServer import OsmApiServer
from Logger import Logger
import DataTable

"""
Supports Updating Places with changes in a GIS dataset

input: 1) OsmChange file (generated with arc2osm or ogr2osm) from a GIS dataset
       2) The history of prior uploads to a given server (A DataTable with a well known schema
       3) A connection to the server where prior/future upload will be made
task: Compare the new upload to prior uploads to determine the features that are new, changed, removed.
output: a new osmChange for uploading to places

Assumptions:
  1) The exact same translator was used to create all OsmChange files for this dataset
  i.e: if translator v1 has poitype='head' => tag {natural:cliff} was used for the initial upload
       and translator v2 has poitype='head' => tag {ammenity:toilet} is used to create the update
       and the features where poitype='head' were not edited in GIS, then they will not be updated in Places
Matrix for Update Actions

+--------+------------------+------------------+---------------+
|  Last  |   GIS Edit Date  |  GIS Edit Date   | GIS Edit Date |
| Action |     Less than    |  not Less than   |   Not Found   |
| in Log | Last Action Date | Last Action Date |    in GIS     |
+--------+------------------+------------------+---------------+
| Create |      Ignore      |     Modify       |    Delete     |
+--------+------------------+------------------+---------------+
| Modify |      Ignore      |     Modify       |    Delete     |
+--------+------------------+------------------+---------------+
| Delete |     Restore[1]   |     Restore      |    Ignore     |
+--------+------------------+------------------+---------------+
|  Not   |                                     |     Not       |
| Found  |                Create               |  Applicable   |
| in log |                                     |               |
+--------+------------------+------------------+---------------+

Create: Feature has never been uploaded to Places, so create in Places
Delete: Feature is in Places, but no longer in GIS; delete in Places
Ignore: GIS feature has not changed since last upload, so no action is required
Modify: Feature has changed in GIS since created or last updated; send changes
Restore: Feature was sent to places, then hidden (deleted from places), and is now unhidden
         feature in places needs to be restored/undeleted.  This is the same as a modify
[1] This can only happen if the translator changed.  Issue warning.

For Delete and Modify, I need to send the current version of the feature to places;
I have the version # of my last change, but the may no longer match places; If the versions
do not match, Places will reject the change.  I need to get the current version from places;
and for modifies, I should merge the changes, with a preference for the GIS changes.
When the version #s do not match, warn the user (and show diff?)
When Deleting Relations/Ways I need to also delete all 'uninteresting' sub elements (nodes and ways)
When modifying a relation/way, I must assume that the GIS shape has changed, I will need to compare all
sub elements and add, delete or modify nodes/ways as necessary.
"""


class Thing:
    def __init__(self, osm_change):
        self.added_nodes = []
        self.added_ways = []
        self.added_relations = []
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        for element in osm_change:
            eid = element.get('id')
            if element.tag == 'relation':
                self.relations[eid] = element
            if element.tag == 'way':
                self.ways[eid] = element
            if element.tag == 'node':
                self.nodes[eid] = element


def copy_root(osm_change):
    """
    Creates a new empty ElementTree representation of the OsmChange file XML

    :param osm_change: Et.Element template for the return value
    :return:
    :rtype : xml.etree.ElementTree.Element
    """
    new_change = Et.Element('osm')
    Et.SubElement(new_change, 'create')
    Et.SubElement(new_change, 'modify')
    Et.SubElement(new_change, 'delete')
    for k, v in osm_change.items():
        new_change.set(k, v)
    return new_change


def make_upload_log_hash(data, date_format='%Y-%m-%d %H:%M:%S.%f'):
    """
    Creates a dictionary from data; data must have the following schema:
    data.fieldnames = ['date_time', 'user_name', 'changeset', 'action', 'element', 'places_id', 'version', 'source_id']
    data.fieldtypes = ['DATE', 'TEXT', 'LONG', 'TEXT', 'TEXT', 'TEXT', 'LONG', 'TEXT'] or all text if from CSV
    There is no error checking in this routine; if the input does not have the expected schema it will crash

    :param data: DataTable with well known schema
    :return: a dictionary of {gis_id: (action, date, places_type, places_id, places_version)}
    :rtype : dict
    """

    upload_data = {}
    for row in data.rows:
        gis_id = row['source_id']
        if type(row['date_time']) == datetime.datetime:
            date = row['date_time']
        else:
            date = datetime.datetime.strptime(row['date_time'], date_format)
        if gis_id in upload_data:
            if date < upload_data[gis_id][1]:
                continue
        action = row['action']
        places_id = row['places_id']
        places_type = row['element']
        if type(row['version']) == int:
            places_version = row['version']
        else:
            places_version = int(row['version'])
        upload_data[gis_id] = (action, date, places_type, places_id, places_version)
    return upload_data


def make_feature_hash(osm_change_create_node, id_key='nps:source_system_key_value',
                      date_key='nps:edit_date', date_format='%Y-%m-%d %H:%M:%S', logger=None):
    """
    Creates a dictionary from the osmChange XML object

    :param osm_change_create_node: the ElementTree representation of the OsmChange file XML
    :param id_key:
    :param date_key:
    :param date_format:
    :param logger:
    :return: a dictionary of {gis_id: (places_type, date, xml_element)}
    :rtype : dict
    """

    feature_data = {}
    for element in osm_change_create_node:
        tags = element.findall('tag')
        if not tags:
            continue
        ptype = element.tag
        gis_id = None
        for tag in tags:
            if tag.attrib['k'] == id_key:
                gis_id = tag.attrib['v']
                break
        if gis_id is None:
            try:
                logger.warn("Skipping element without a source_id '{0}' tag".format(id_key))
            except AttributeError:
                pass
            continue
        date_str = None
        for tag in tags:
            if tag.attrib['k'] == date_key:
                date_str = tag.attrib['v']
                break
        if date_str is None:
            try:
                msg = "Feature {0}: No '{1}' tag. Assuming edited recently."
                logger.warn(msg.format(gis_id, date_key))
            except AttributeError:
                pass
            date = None
        else:
            try:
                # TODO: make date handling more robust
                date_str = date_str.split('.')[0]  # remove optional trailing spaces
                date = datetime.datetime.strptime(date_str, date_format)
            except ValueError:
                try:
                    msg = "Feature {0}: Unexpected date format '{1}'. Assuming edited recently."
                    logger.warn(msg.format(gis_id, date_str))
                except AttributeError:
                    pass
                date = None
        feature_data[gis_id] = (ptype, date, element)
    return feature_data


def create(new_change, thing, element, logger=None):
    """
    Copy element from osm_change into new_change; need to recursively copy the sub elements

    :param new_change: an ElementTree representation of the new OsmChange file XML
    :param thing: an internal formatting of the proposed OsmChange file
    :param element: the element in the osmChange to copy to newChange
    :return: None
    """
    # print 'create'
    # Et.dump(element)
    if element.tag == 'relation':
        rid = element.get('id')
        if rid not in thing.added_relations:
            # recursively add all the sub elements of a relation
            for member in element.findall('member'):
                mtype = member.get('type')
                mid = member.get('ref')
                if mtype == 'relation':
                    subelement = thing.relations[mid]
                elif mtype == 'way':
                    subelement = thing.ways[mid]
                else:
                    subelement = thing.nodes[mid]
                create(new_change, thing, subelement, logger)
            # Add the relation and all it's references/tags
            new_change.insert(len(thing.added_nodes) + len(thing.added_ways) + len(thing.added_relations), element)
            thing.added_relations.append(rid)

    if element.tag == 'way':
        wid = element.get('id')
        if wid not in thing.added_ways:
            # add all the nodes of a way
            for node in element.findall('nd'):
                nid = node.get('ref')
                if nid not in thing.added_nodes:
                    subelement = thing.nodes[nid]
                    new_change.insert(len(thing.added_nodes), subelement)
                    thing.added_nodes.append(nid)
            # add the way
            new_change.insert(len(thing.added_nodes) + len(thing.added_ways), element)
            thing.added_ways.append(wid)

    if element.tag == 'node':
        nid = element.get('id')
        if nid not in thing.added_nodes:
            new_change.insert(len(thing.added_nodes), element)
            thing.added_nodes.append(nid)
    return


def delete(new_change, thing, pserver, ptype, pid, pversion, logger=None):
    """
    Adds a delete elemnt to new_change

    :param new_change:
    :param thing:
    :param pserver:
    :param ptype:
    :param pid:
    :param pversion:
    :param logger:
    :return:
    """

    """
    delete_xml = Et.Element('delete')
    for [(element_type, places_id)]:
        delete_xml = create delete node
        for element_type, places_id in [(element_type, places_id)]:
           element_xml = places.get_element_xml('http://10.147.153.193/api/0.6/{{element_type}}/{{places_id}}/full')
                # removes ways from relation if they are in other relations
                #   if get /api/0.6/way/#id/relations > 1
                # removes nodes if they are in other ways or relations (maybe only check first/last nodes):
                #   if get http://10.147.153.193/api/0.6/node/{node}/ways > 1
                #
                # alternative (less load on server) support DELETE /api/0.6/[node|way|relation]/#id
                #   nice to remove version from payload, and skip sub-elements which are in use or interesting
    delete_xml.append(element_xml)
    xml.append(delete_xml)
    """

    # FIXME: Implement
    # print 'delete', ptype, pid, pversion
    return


def restore(new_change, thing, element, pserver, ptype, pid, pversion, logger=None):
    """
    Undeletes an element in places (modifies it back to visible)

    :param new_change:
    :param thing:
    :param element:
    :param pserver:
    :param ptype:
    :param pid:
    :param pversion:
    :param logger:
    :return:
    """

    # FIXME: Implement
    # print 'restore', ptype, pid
    # Et.dump(element)
    return


def modify(new_change, thing, element, pserver, ptype, pid, pversion, logger=None):
    """
    Merges the new and the old places item into a new 'modify' element in new_change

    :param new_change:
    :param thing:
    :param element:
    :param pserver:
    :param ptype:
    :param pid:
    :param pversion:
    :param logger:
    :return:
    """

    """
      # for each feature get the existing data from places
      #   (http://10.147.153.193/api/0.6/{{element_type}}/{{places_id}}/full)
      # (optional) need to add any attributes in places that are not in eGIS (or they will get removed)
      # compare ways/nodes in relationships one by one, and move to 'delete' any elements in places but
      #   not in GIS, need to check if used in other relationships
      # compare vertices in ways one by one, and move to 'delete' any elements in places but not in GIS,
      #     need to check if used in other ways/relationships
      #     and (optionally) remove any from update if there is no change
      #     maybe do not remove the sub element from the way/relationship,
      #     but keep in places - it should probably be removed if it is unused and uninteresting
      #     (maybe happens in a places cleanup)
      # update the version number place holder from arc2osm with the correct version number from places
    """

    # FIXME: Implement
    # print 'modify', ptype, pid
    # Et.dump(element)
    return


def build(osm_change, upload_log, server, logger=None):
    new_change = copy_root(osm_change)
    # Et.dump(new_change)
    osm_change_create_node = osm_change[0]
    new_change_create_node = new_change[0]
    new_change_modify_node = new_change[1]
    new_change_delete_node = new_change[2]
    thing = Thing(osm_change_create_node)
    # Et.dump(osm_change_create_node)
    features = make_feature_hash(osm_change_create_node, logger=logger)
    # print features
    updates = make_upload_log_hash(upload_log)
    # print updates
    for gis_id in features:
        if gis_id not in updates:
            create(new_change_create_node, thing, features[gis_id][2], logger)
    for gis_id in features:
        if gis_id in updates:
            if updates[gis_id][0] == 'delete':
                if features[gis_id][0] != updates[gis_id][2]:
                    msg = "Cannot update id '{0} from a {1} to a {2}"
                    msg = msg.format(gis_id, features[gis_id][0], updates[gis_id][2])
                    try:
                        logger.error(msg)
                    except AttributeError:
                        pass
                    continue
                if features[gis_id][1] < updates[gis_id][1]:
                    msg = "Translator has changed if feature '{0}' is no longer hidden with no edits".format(gis_id)
                    try:
                        logger.warn(msg)
                    except AttributeError:
                        pass
                restore(new_change_modify_node, thing, features[gis_id][2],
                        server, updates[gis_id][2], updates[gis_id][3], updates[gis_id][4], logger)
            if updates[gis_id][0] in ['create', 'modify']:
                if (updates[gis_id][1] is None or features[gis_id][1] is None
                        or updates[gis_id][1] <= features[gis_id][1]):
                    if features[gis_id][0] != updates[gis_id][2]:
                        msg = "Cannot update id '{0} from a {1} to a {2}"
                        msg = msg.format(gis_id, features[gis_id][0], updates[gis_id][2])
                        try:
                            logger.error(msg)
                        except AttributeError:
                            pass
                        continue
                    modify(new_change_modify_node, thing, features[gis_id][2],
                           server, updates[gis_id][2], updates[gis_id][3], updates[gis_id][4], logger)
    for gis_id in updates:
        if gis_id not in features:
            if updates[gis_id][0] in ['create', 'modify']:
                delete(new_change_delete_node, thing,
                       server, updates[gis_id][2], updates[gis_id][3], updates[gis_id][4], logger)
    if not list(new_change_create_node):
        new_change.remove(new_change_create_node)
    if not list(new_change_modify_node):
        new_change.remove(new_change_modify_node)
    if not list(new_change_delete_node):
        new_change.remove(new_change_delete_node)
    return new_change


def test():
    osm_change_file = './testdata/update_test1.osm'
    update_log_csv = './testdata/update_test1.csv'
    new_change_file = './testdata/update_test1_out.osm'

    osm_change = Et.parse(osm_change_file).getroot()
    update_log = DataTable.from_csv(update_log_csv)
    api_server = OsmApiServer('test')
    api_server.logger = Logger()
    api_server.logger.start_debug()

    new_change = build(osm_change, update_log, api_server, api_server.logger)

    data = Et.tostring(new_change, encoding='utf-8')
    with open(new_change_file, 'w') as fw:
        fw.write(data)
    print "Done."


def cmdline():
    # Setup program usage
    usage = """%prog [Options] SRC LOG DST
    or:    %prog --help

    Creates a file called DST from changes in SRC compared to LOG.
    SRC is an ArcGIS feature class
    LOG is an ArcGIS table that describes the features sent to places
    DST is a OSM change file
    """

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-s", "--server", dest="server", type=str, help=(
        "Name of server to connect to. I.e. 'places', 'osm', 'osm-dev', 'local'." +
        "Defaults to 'places'.  Name must be defined in the secrets file."), default='places')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="Write processing step details to stdout.")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="Write debugging details to stdout.")
    parser.add_option("--changeset-id", dest="changesetId", type=int,
                      help="Sentinal ID number for the changeset.  Only used " +
                           "when an osmChange file is being created. " +
                           "Defaults to -1.", default=-1)

    parser.set_defaults(verbose=False, debug=False)

    # Parse and process arguments
    (options, args) = parser.parse_args()

    if len(args) < 3:
        parser.error(u"You must specify a source, log and destination")
    elif len(args) > 3:
        parser.error(u"You have specified too many arguments.")

    # Input and output file
    osm_change_file = args[0]
    update_log_csv = args[1]
    new_change_file = args[2]
    if os.path.exists(new_change_file):
        parser.error(u"The destination file exist.")

    # API Server
    if options.server:
        api_server = OsmApiServer(options.server)
    else:
        api_server = OsmApiServer('places')
    online = api_server.is_online()
    if api_server.error:
        print api_server.error
        sys.exit(1)
    if not online:
        print "Server is not online right now, try again later."
        sys.exit(1)
    if not api_server.is_version_supported():
        print "Server does not support version " + api_server.version + " of the OSM"
        sys.exit(1)

    #verbose/debug
    if options.verbose or options.debug:
        logger = Logger()
        if options.debug:
            logger.start_debug()
        api_server.logger = logger

    # Changeset ID option
    # TODO: implement or delete

    # Build Change XML
    # TODO: Add error checking
    osm_change = Et.parse(osm_change_file).getroot()
    update_log = DataTable.from_csv(update_log_csv)
    new_change = build(osm_change, update_log, api_server, api_server.logger)

    # write output
    data = Et.tostring(new_change, encoding='utf-8')
    with open(new_change_file, 'w') as fw:
        fw.write(data)
    print "Done."


if __name__ == '__main__':
    test()
    # cmdline()
