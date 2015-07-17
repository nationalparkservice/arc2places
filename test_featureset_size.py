import arcpy
import arcpy.da
import os

src = os.path.join("Database Connections",
                   # "akr_facility_on_inpakrovmais_as_gis.sde",
                   # "akr_facility_on_inpakrovmais_as_sde.sde",
                   "akr_facility_on_inpakrovmais_as_akr_reader_web.sde",
                   # "akr_facility.gis.trails_ln")
                   "akr_facility.gis.roads_ln")
print src
feature_count = 0
vertex_count = 0
max_vertices = 0
where = "DISTRIBUTE = 'Public' and RESTRICTION = 'Unrestricted' AND INPLACES = 'Yes'"
# where = "DISTRIBUTE = 'Yes' and RESTRICTION = 'Unrestricted' AND LOCATIONID IS NOT NULL"
# with arcpy.da.SearchCursor(src, ['SHAPE@', 'OID@']) as cursor:
with arcpy.da.SearchCursor(src, ['SHAPE@'], where) as cursor:
    for feature in cursor:
        #feature_count += 1
        # print feature_count, feature[0], vertex_count, max_vertices
        geom = feature[0]
        if geom and geom.type == 'polyline' and not geom.isMultipart:
            part = geom.getPart(0)
            vertices = len(part)
            feature_count += 1
            vertex_count += vertices
            if max_vertices < vertices:
                max_vertices = vertices
            # print feature_count, feature[0], vertex_count, max_vertices
            #print feature_count, vertex_count, max_vertices
        else:
            if geom:
                print "unexpected geometry", geom.type, "multipart", geom.isMultipart
            else:
                print "geometry is null"

print "line_count", feature_count
print "vertex_count", vertex_count
print "changeset_size", feature_count + vertex_count
print "max_vertices", max_vertices
