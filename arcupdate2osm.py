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
        # Keep track of which nodes ids have been added to each block, so we do not have repeats
        self.added = {
            'create': {
                'node': [],
                'way': [],
                'relation': [],
            },
            'modify': {
                'node': [],
                'way': [],
                'relation': [],
            },
            'delete': {
                'node': [],
                'way': [],
                'relation': [],
            }
        }
        # all elements by id in the input file
        self.elements = {
            'node': {},
            'way': {},
            'relation': {}
        }

        self.osm_change = osm_change
        self.new_change = None
        self.new_change_nodes = {}
        self.copy_root()
        self.build_dicts()

    def copy_root(self):
        # Creates a new empty ElementTree representation of the OsmChange file XML
        self.new_change = Et.Element('osmChange')
        for k, v in self.osm_change.items():
            self.new_change.set(k, v)
        for block in ['create', 'modify', 'delete']:
            self.new_change_nodes[block] = Et.SubElement(self.new_change, block)

    def build_dicts(self):
        for element in self.osm_change[0]:
            eid = element.get('id')
            etype = element.tag
            self.elements[etype][eid] = element

    def conditional_add(self, element, to):
        etype = element.tag
        eid = element.get('id')
        # print 'adding', etype, eid, to
        if eid in self.added[to][etype]:
            return False
        index = len(self.added[to]['node'])
        if etype != 'node':
            index += len(self.added[to]['way'])
        if etype == 'relation':
            index += len(self.added[to]['relation'])
        element.set('changeset', '-1')
        if to == 'modify':
            element.set('visibility', 'true')
        self.new_change_nodes[to].insert(index, element)
        self.added[to][etype].append(eid)
        return True

    def remove_unused_lists(self):
        for block in ['create', 'modify', 'delete']:
            if not list(self.new_change_nodes[block]):
                self.new_change.remove(self.new_change_nodes[block])


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
        # All versions returned by server are strings, so use string to simplify
        places_version = str(row['version'])
        upload_data[gis_id] = (action, date, places_type, places_id, places_version)
    return upload_data


def make_feature_hash(osm_change, id_key='nps:source_system_key_value',
                      date_key='nps:edit_date', date_format='%Y-%m-%d %H:%M:%S', logger=None):
    """
    Creates a dictionary from the osmChange XML object

    :param osm_change: the ElementTree representation of the OsmChange file XML
    :param id_key:
    :param date_key:
    :param date_format:
    :param logger:
    :return: a dictionary of {gis_id: (places_type, date, xml_element)}
    :rtype : dict
    """

    osm_change_create_node = osm_change[0]
    feature_data = {}
    for element in osm_change_create_node:
        tags = element.findall('tag')
        if not tags:
            continue
        ptype = element.tag
        gis_id = None
        for tag in tags:
            if tag.get('k') == id_key:
                gis_id = tag.get('v')
                break
        if gis_id is None:
            try:
                logger.warn("Skipping element without a source_id '{0}' tag".format(id_key))
            except AttributeError:
                pass
            continue
        date_str = None
        for tag in tags:
            if tag.get('k') == date_key:
                date_str = tag.get('v')
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


def get_element_from_server_as_xml(pserver, ptype, pid, logger=None, details=None):
    # TODO: add more error checking
    # TODO: only some places servers support 'uninteresting' details
    element_str = pserver.get_element(ptype, pid, details)
    if element_str is None:
        try:
            msg = "{0} {1} not found on Server '{2}'. Skipping..."
            logger.error(msg.format(ptype, pid, pserver.name))
        except AttributeError:
            pass
        return
    element_xml = Et.fromstring(element_str.encode('utf-8'))
    element = element_xml
    return element


def create(thing, element, logger=None):
    """
    Conditionally add element to the create block in thing; then add referenced elements

    :param thing: an internal formatting of the proposed OsmChange file
    :param element: the element in the osmChange to add to the create block
    :return: None
    """
    try:
        logger.debug('create {0}'.format(element.get('id')))
        logger.debug(Et.tostring(element))
    except AttributeError:
        pass

    added = thing.conditional_add(element, to='create')
    if element.tag == 'way' and added:
        for node_ref in element.findall('nd'):
            nid = node_ref.get('ref')
            node = thing.elements['node'][nid]
            thing.conditional_add(node, to='create')
    if element.tag == 'relation' and added:
        # Note, this is non-streamable. parent relation is written before child relations
        # elements in blocks do not need to be sorted (http://wiki.openstreetmap.org/wiki/OSM_XML)
        # TODO: test unstreamable relations on places-api (note: places may not even support super relations)
        # recursively add all the sub elements of a relation
        for member in element.findall('member'):
            mtype = member.get('type')
            mid = member.get('ref')
            subelement = thing.elements[mtype][mid]
            create(thing, subelement, logger)
    return


def delete(thing, pserver, ptype, pid, pversion, logger=None):
    """
    Get element from the server then Conditionally add it to the delete block in thing; then add referenced elements

    :param thing:
    :param pserver:
    :param ptype:
    :param pid:
    :param pversion:
    :param logger:
    :return:
    """
    try:
        logger.debug('delete {0} {1} {2}'.format(ptype, pid, pversion))
    except AttributeError:
        pass
    # return

    def delete_element(element):
        added = thing.conditional_add(element, to='delete')
        if element.tag == 'way' and added:
            for node_ref in element.findall('nd'):
                nid = node_ref.get('ref')
                node = elements['node'].get(nid)
                # node may not exist because it is interesting (i.e. it has tags or is being used)
                if node is not None:
                    thing.conditional_add(node, to='delete')
        if element.tag == 'relation' and added:
            # recursively add all the sub elements of a relation
            for member in element.findall('member'):
                mtype = member.get('type')
                mid = member.get('ref')
                subelement = thing.elements[mtype].get(mid)
                if subelement is not None:
                    delete_element(subelement)

    # FIXME: This only works on places-api servers
    # TODO: on real 0.6 API servers get full details and use 'if-unused' attribute in delete block
    # TODO: investigate adding 'if-unused' support to places-api
    # TODO: places-api algorithm may leave orphans.  e.g. if way1 and way2 both use a node, and they are deleted together
    # places-api does not support 'if-unused' however, it does have a special 'uninteresting' call instead
    osm = get_element_from_server_as_xml(pserver, ptype, pid, logger=logger, details='uninteresting')
    if osm is None:
        return
    main_element = osm[0]
    version = main_element.get('version')
    if version != pversion:
        try:
            user = main_element.get('user')
            msg = "{0} {1}v{2} found expected v{3}. Deleting edits by {4}."
            logger.warn(msg.format(ptype, pid, version, pversion, user))
        except AttributeError:
            pass

    # build dicts of elements by id for easy reference
    elements = {
        'node': {},
        'way': {},
        'relation': {}
    }
    for osm_element in osm.findall('./'):
        etype = osm_element.tag
        eid = osm_element.get('id')
        elements[etype][eid] = osm_element

    delete_element(main_element)
    return


def restore(thing, element, pserver, ptype, pid, pversion, logger=None, merge=True, decimals=7):
    """
    Un-deletes an element in places (modifies it back to visible)

    Since the element may have more changes than just visibility we need to do a full modify
    The modify routine needs to add existing otherwise unchanged elements to
    the modify section so that the visibility flag can be set.

    parameters are the same as modify()
    No return value
    """
    try:
        logger.debug('restore {0} {1}'.format(ptype, pid))
        logger.debug(Et.tostring(element))
    except AttributeError:
        pass

    modify(thing, element, pserver, ptype, pid, pversion, logger=logger,
           merge=merge, decimals=decimals, undelete=True)


def modify(thing, element, pserver, ptype, pid, pversion, logger=None, merge=True, decimals=7, undelete=False):
    """
    Merges the new and the old places item into a new 'modify' element in new_change

    :param thing:
    :param element:
    :param pserver:
    :param ptype:
    :param pid:
    :param pversion:
    :param logger:
    :return:
    """
    try:
        logger.debug('modify {0} {1}'.format(ptype, pid))
        logger.debug(Et.tostring(element))
    except AttributeError:
        pass
    # return

    def version_check(old_element, new_element_version):
        # Check version and print warning if mis match, return True if they are the same
        old_element_version = old_element.get('version')
        if old_element_version != new_element_version:
            msg = ("Feature (Places ID = {0}) has been edited in Places since last update: "
                   "Last update = version {1}, Places = version {2}. "
                   "Changes to geometry in Places will be overwritten with this update. ")
            if merge:
                msg += "Tags will be merged with conflicts resolving in favor of this update."
            else:
                msg += "All tags in Places will be replaced with the tags in this update."
            msg = msg.format(pid, new_element_version, old_element_version)
            try:
                logger.warn(msg)
            except AttributeError:
                pass
        return old_element_version == new_element_version

    def merge_tags(old_element, new_element):
        # Add tags from old_element to new_element if not found in new_element
        new_keys = [new_tag.get('k') for new_tag in new_element.findall('tag')]
        for old_tag in old_element.findall('tag'):
            old_key = old_tag.get('k')
            if old_key not in new_keys:
                new_tag = Et.SubElement(new_element, 'tag')
                new_tag.set('k', old_key)
                new_tag.set('v', old_tag.get('v'))

    def update_way_nodes(old_full_way, new_way):
        """
        Node are compared by their (x,y) values (location match),
        and then by their sequence number in the gaps between identity matching nodes (sequence match)
        1) walk the nd refs in way, by replacing the temp id with places id when there is a location match
        2) walk the nd refs in way, by replacing the temp id with places id when there is a sequence match
           modify/update the (x,y) values in the existing node to (x,y) from the new node
        3) add the unmatched nodes in way to the create block
        4) delete unmatched nodes in old_way (if they have no tags)
        """
        identity_match = {}
        sequence_match = {}
        unmatched_old_nodes = []
        unmatched_new_nodes = []
        used_temp_ids = set()
        used_exist_ids = set()

        def get_hashable_location(node):
            # I'm using the location as a hash key,
            # values in OSM file are string representations of floats.
            # floats should not be used for equality testing, so they make a bad hash key.
            # strings are good, but they they would need to be normalized i.e. "1.23" == "1.230".
            # ints are better (smaller), when they are normalized
            # need to make sure I'm rounding, not truncating
            lat = node.get('lat')
            b, m = lat.split('.')
            y = int(b + (m + '0'*decimals)[:decimals])
            if len(m) > decimals and m[decimals] > "4":
                y += 1
            lon = node.get('lon')
            b, m = lon.split('.')
            x = int(b + (m + '0'*decimals)[:decimals])
            if len(m) > decimals and m[decimals] > "4":
                x += 1
            return x, y

        # Find Identity Matches
        matching_indexes = []  # needed for next step (find sequence matches)
        old_node_locations = {}
        old_nodes = {}
        # the node elements are not in way order; but I need way order to compare with the new way
        for item in old_full_way.findall('node'):
            old_nodes[item.get('id')] = item
        new_node_list = list(new_way.findall('nd'))
        old_node_list = list(old_full_way.find('way').findall('nd'))
        for old_index in range(len(old_node_list)):
            old_node_ref = old_node_list[old_index]
            old_node_id = old_node_ref.get('ref')
            old_node = old_nodes[old_node_id]
            xy = get_hashable_location(old_node)
            old_node_locations[xy] = (old_node_id, old_index, old_node)
        for new_index in range(len(new_node_list)):
            new_node_ref = new_node_list[new_index]
            temp_id = new_node_ref.get('ref')
            new_node = thing.elements['node'][temp_id]
            xy = get_hashable_location(new_node)
            if xy in old_node_locations:
                used_temp_ids.add(temp_id)
                existing_id, old_index, old_node = old_node_locations[xy]
                used_exist_ids.add(existing_id)
                identity_match[existing_id] = (new_node_ref, old_node)
                matching_indexes.append((new_index, old_index))

        # Find Sequence Matches
        def add_match(n_index, o_index):
            nd_ele = new_node_list[n_index]
            t_id = nd_ele.get('ref')
            o_node = old_node_list[o_index]
            e_id = old_node.get('id')
            n_node = thing.elements['node'][t_id]
            sequence_match[e_id] = (t_id, nd_ele, o_node, n_node)

        new_index = 0
        old_index = 0
        matching_indexes.append((len(new_node_list), len(old_node_list)))
        for next_match_new, next_match_old in matching_indexes:
            while new_index < next_match_new and old_index < next_match_old:
                add_match(new_index, old_index)
                old_index += 1
                new_index += 1
            new_index = next_match_new + 1
            old_index = next_match_old + 1

        # update unused lists
        for (existing_id, (temp_id, nd_element, old_node, new_node)) in sequence_match.items():
                used_temp_ids.add(temp_id)
                used_exist_ids.add(existing_id)

        # Find unmatched Nodes:
        for old_node in old_full_way.findall('node'):
            eid = old_node.get('id')
            if eid not in used_exist_ids:
                unmatched_old_nodes.append(old_node)
        for new_node_ref in new_way.findall('nd'):
            temp_id = new_node_ref.get('ref')
            if temp_id not in used_temp_ids:
                unmatched_new_nodes.append(thing.elements['node'][temp_id])

        # Step 1
        for (existing_id, (nd_element, old_node)) in identity_match.items():
            nd_element.set('ref', existing_id)
            # node exists in places already, so do not add to OSM file, unless this is a restore
            if undelete:
                thing.conditional_add(old_node, to='modify')

        # Step 2
        for (existing_id, (temp_id, nd_element, old_node, new_node)) in sequence_match.items():
            nd_element.set('ref', existing_id)
            old_node.set('lat', new_node.get('lat'))
            old_node.set('lon', new_node.get('lon'))
            old_node.set('changeset', '-1')
            # node exists in places but is being modified
            thing.conditional_add(old_node, to='modify')

        # Step 3
        for new_node in unmatched_new_nodes:
            # nd ref exists, and contains same temp id as node
            thing.conditional_add(new_node, to='create')

        # Step 4
        ids_unused_nodes = set()  # 'id's of nodes in this way that are unused by other ways/relations
        if len(unmatched_old_nodes) > 0:
            # FIXME: This only works on places-api servers; alternative is to used 'if-unused' in delete block;
            osm = get_element_from_server_as_xml(pserver, ptype, pid, logger=logger, details='uninteresting')
            if osm is not None:
                ids_unused_nodes = set([node.get('id') for node in osm.findall('node')])


        for old_node in unmatched_old_nodes:
            # nothing to update on the way, since there is no nd ref for this deleted node
            used = False  # FIXME: Need to check with the server; deleting a used node will fail
            if not old_node.find('tag') and not used:
                old_node.set('changeset', '-1')
                thing.conditional_add(old_node, to='delete')

    def update_relation_ways(old_relation_full, new_relation):
        # FIXME: Implement
        pass

    # main logic of update procedure
    server_element = get_element_from_server_as_xml(pserver, ptype, pid, logger=logger, details='full')
    if server_element is None:
        return
    # for node looks like <osm><node ... /></osm>
    # for way looks like <osm><way ... /><node 1 />...<node n/></osm>
    # for relation looks like <osm><relation ... />...<rel n><way 1/>...<way n /><node 1 />...<node n/></osm>
    #     does NOT return the ways and nodes in referenced relations
    main_element = server_element[0]
    element.set('version', main_element.get('version'))
    element.set('id', main_element.get('id'))
    match = version_check(main_element, pversion)
    if not match and merge:
        merge_tags(main_element, element)
    if ptype == 'way':
        update_way_nodes(server_element, element)
    if ptype == 'relation':
        update_relation_ways(server_element, element)
    thing.conditional_add(element, to='modify')
    return


def build(osm_change, updates, server, logger=None):
    thing = Thing(osm_change)
    features = make_feature_hash(osm_change, logger=logger)
    try:
        logger.debug('features')
        logger.debug(str(features))
    except AttributeError:
        pass

    # find new features (create block)
    for gis_id in features:
        if gis_id not in updates:
            create(thing, features[gis_id][2], logger)

    # find modified features (modify block)
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
                restore(thing, features[gis_id][2],
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
                    modify(thing, features[gis_id][2],
                           server, updates[gis_id][2], updates[gis_id][3], updates[gis_id][4], logger)

    # find deleted features (delete block)
    for gis_id in updates:
        if gis_id not in features:
            if updates[gis_id][0] in ['create', 'modify']:
                delete(thing, server, updates[gis_id][2], updates[gis_id][3], updates[gis_id][4], logger)

    # remove unused blocks
    thing.remove_unused_lists()
    return thing.new_change


def read_build_write(osm_change_file, update_log_csv, new_change_file, api_server, logger=None):

    error_logger = Logger()
    # Build Change XML; will throw an error if input is no good
    try:
        logger.info(u'Read OsmChange file')
    except (AttributeError, TypeError):
        pass
    try:
        osm_change = Et.parse(osm_change_file).getroot()
    except:
        try:
            error_logger.error("File {0} is not be valid OsmChange file.".format(osm_change_file))
        except AttributeError:
            pass
        raise

    # Read the upload log CSV; will throw an error if input is no good
    try:
        logger.info(u'Read CSV file')
    except (AttributeError, TypeError):
        pass
    try:
        update_log = DataTable.from_csv(update_log_csv)
    except:
        error_logger.error("File {0} is not a valid CSV file.".format(update_log_csv))
        raise

    # Build the upload log from CSV; will throw an error if input is no good
    try:
        logger.info(u'Process Update Log')
    except (AttributeError, TypeError):
        pass
    try:
        updates = make_upload_log_hash(update_log)
    except:
        error_logger.error("File {0} does not have the expected upload log format.".format(update_log_csv))
        raise
    try:
        logger.debug('updates')
        logger.debug(str(updates))
    except (AttributeError, TypeError):
        pass

    # Build the new change file; If it throw it is an unexpected programming error, so just crash
    try:
        logger.info(u'Build OsmChange data')
    except (AttributeError, TypeError):
        pass
    new_change = build(osm_change, updates, api_server, logger)

    # write output
    try:
        logger.info(u'Write OsmChange to file')
    except (AttributeError, TypeError):
        pass
    data = Et.tostring(new_change, encoding='utf-8')
    with open(new_change_file, 'w') as fw:
        fw.write(data)


def test():
    # You need to uncomment the first few lines of the 4 major functions to when doing the first test
    tests = [
        #('create/modify/delete logic test', 'update_test1'),
        #('create test', 'update_test2'),
        #('delete test', 'test_roads2'),
        ('modify test', 'update_test3'),
    ]
    for (testname, testfile) in tests:
        print '*'*40
        print testname
        print '*'*40

        osm_change_file = './testdata/' + testfile + '.osm'
        update_log_csv = './testdata/' + testfile + '.csv'
        new_change_file = './testdata/' + testfile + '_out.osm'

        logger = Logger()
        logger.start_debug()
        api_server = OsmApiServer('mac')
        api_server.logger = logger
        read_build_write(osm_change_file, update_log_csv, new_change_file, api_server, logger)
    print 'Done.'


def cmdline():
    # Setup program usage
    usage = """%prog [Options] SRC LOG DST
    or:    %prog --help

    Create an OsmChange file for updates to a prior upload.
    SRC is an OsmChange file for a GIS data set, created with {ogr|arc}2osm
    LOG is a CSV file of features sent to places, created with arc2places
    DST is the new OsmChange file to create, must not exist.
    """

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-s", "--server", dest="server", type=str, help=(
        "Name of server to connect to. I.e. 'places', 'test', 'osm', 'osm-dev'." +
        "Defaults to 'test'.  Name must be defined in the secrets file."), default='test')
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="Write processing step details to stdout.")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="Write debugging details to stdout.")
    parser.set_defaults(verbose=False, debug=False)

    # Parse and process arguments
    (options, args) = parser.parse_args()

    logger = Logger()
    if options.debug:
        options.verbose = True
        logger.start_debug()
    logger.debug("args: " + str(args))
    logger.debug("options: " + str(options))

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
        api_server = OsmApiServer('test')
    if api_server.error:
        logger.error(api_server.error)
        sys.exit(1)
    if options.verbose or options.debug:
        api_server.logger = logger
    online = api_server.is_online()
    if api_server.error:
        logger.error(api_server.error)
        sys.exit(1)
    if not online:
        logger.error("Server is not online right now, try again later.")
        sys.exit(1)
    if not api_server.is_version_supported():
        logger.error("Server does not support version {0} of the OSM API".format(api_server.version))
        sys.exit(1)

    read_build_write(osm_change_file, update_log_csv, new_change_file, api_server, api_server.logger)


if __name__ == '__main__':
    # test()
    cmdline()
