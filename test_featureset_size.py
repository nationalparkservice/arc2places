import arcpy
import arcpy.da
import os


def old_school(src):
    print src
    feature_count = 0
    vertex_count = 0
    max_vertices = 0
    where = "(DISTRIBUTE = 'Public' and RESTRICTION = 'Unrestricted') or INPLACES = 'Yes'"
    cursor = arcpy.SearchCursor(src, where, fields='SHAPE, OBJECTID')
    for row in cursor:
        geom = row.getValue('SHAPE')  # None #feature[0]
        if geom and geom.type == 'polyline' and not geom.isMultipart:
            part = geom.getPart(0)
            vertices = len(part)
            feature_count += 1
            vertex_count += vertices
            if max_vertices < vertices:
                max_vertices = vertices
        else:
            if geom:
                print row.getValue('OBJECTID'), "unexpected geometry", geom.type, "multipart", geom.isMultipart
            else:
                print "geometry is null"

    print "line_count", feature_count
    print "vertex_count", vertex_count
    print "changeset_size", feature_count + vertex_count
    print "max_vertices", max_vertices


def new_school(src):
    print src
    feature_count = 0
    vertex_count = 0
    max_vertices = 0
    where = "(DISTRIBUTE = 'Public' and RESTRICTION = 'Unrestricted') or INPLACES = 'Yes'"
    with arcpy.da.SearchCursor(src, ['SHAPE@', 'OID@'], where) as cursor:
        for feature in cursor:
            geom = feature[0]
            if geom and geom.type == 'polyline' and not geom.isMultipart:
                part = geom.getPart(0)
                vertices = len(part)
                feature_count += 1
                vertex_count += vertices
                if max_vertices < vertices:
                    max_vertices = vertices
                    print feature_count, feature[1], vertex_count, max_vertices
            else:
                if geom:
                    print feature[1], "unexpected geometry", geom.type, "multipart", geom.isMultipart
                else:
                    print "geometry is null"

    print "line_count", feature_count
    print "vertex_count", vertex_count
    print "changeset_size", feature_count + vertex_count
    print "max_vertices", max_vertices


def main():
    src = os.path.join("Database Connections",
                       # "akr_facility_on_inpakrovmais_as_gis.sde",
                       # "akr_facility_on_inpakrovmais_as_sde.sde",
                       "akr_facility_on_inpakrovmais_as_akr_reader_web.sde",
                       "akr_facility.gis.trails_ln")  # "akr_facility.gis.roads_ln")

    # This crashes python (2.7.5 - 32bit) with an access violation. (ArcGIS 10.3.0.4284)
    # it crashes if the shape (in any form) is in the result set and only with the trails dataset
    # the crash occurs when iterating the cursor - usually at the same place, but not always.
    # It can crash when only a single feature is returned in the where clause. (OID = 64077, 64161, 64297, 64916)
    # arcpy.SearchCursor() does not exhibit this problem.
    # new_school(src)

    old_school(src)


if __name__ == '__main__':
    main()
