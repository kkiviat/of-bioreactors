"""Utility methods to help Salome construct bioreactor geometries."""
import math

import GEOM


def makeAxes(geompy, plane_trim=100):
    O = geompy.MakeVertex(0, 0, 0, theName="O")
    OX = geompy.MakeVectorDXDYDZ(1, 0, 0, theName="OX")
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0, theName="OY")
    OZ = geompy.MakeVectorDXDYDZ(0, 0, 1, theName="OZ")
    OXY = geompy.MakePlane2Vec(OX, OZ, plane_trim, theName="OXY")
    OYZ = geompy.MakePlane2Vec(OY, OX, plane_trim, theName="OYZ")
    OXZ = geompy.MakePlane2Vec(OX, OY, plane_trim, theName="OXZ")
    return O, OX, OY, OZ, OXY, OYZ, OXZ


def normalizeVector(vector, geompy):
    return geompy.Scale(vector, None, 1 / math.sqrt(geompy.dot(vector, vector)))


def getPlaneHeight(horizontalPlane, geompy):
    vertices = geompy.SubShapeAllSortedCentres(
        horizontalPlane, geompy.ShapeType["VERTEX"]
    )
    return geompy.PointCoordinates(vertices[0])[1]


def makeHexagon(side_length, geompy):
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0, theName="OY")
    p1 = geompy.MakeVertex(side_length, 0, 0, theName="p1")
    p2 = geompy.MakeRotation(p1, OY, -math.pi / 3, "p2")
    p3 = geompy.MakeRotation(p2, OY, -math.pi / 3, "p3")
    p4 = geompy.MakeRotation(p3, OY, -math.pi / 3, "p4")
    p5 = geompy.MakeRotation(p4, OY, -math.pi / 3, "p5")
    p6 = geompy.MakeRotation(p5, OY, -math.pi / 3, "p6")
    hex = makeFace([p1, p2, p3, p4, p5, p6], geompy)
    return hex


def makeFace(points, geompy):
    lines = []
    for i in range(len(points) - 1):
        lines.append(geompy.MakeLineTwoPnt(points[i], points[i + 1]))
    lines.append(geompy.MakeLineTwoPnt(points[-1], points[0]))
    return geompy.MakeFaceWires(lines, 1)


def horizontalPlane(height, geompy, plane_trim=10):
    return geompy.MakePlane(
        geompy.MakeVertex(0, height, 0),
        geompy.MakeVectorDXDYDZ(0, 1, 0),
        plane_trim,
    )


def shapeBelowHeight(shape, height, geompy, height_axis):
    """
    Cuts the shape to the part below "height" along the given height_axis.

    height_axis = 0 for x-axis, 1 for y-axis, 2 for z-axis
    """
    if height_axis == 0:
        [Xmin, Xmax, Ymin, Ymax, Zmin, Zmax] = geompy.BoundingBox(shape)
        cut_box = geompy.MakeBox(
            height,
            Ymin - 1,
            Zmin - 1,
            Xmax + 1,
            Ymax + 1,
            Zmax + 1,
        )
    elif height_axis == 1:
        [Xmin, Xmax, Ymin, Ymax, Zmin, Zmax] = geompy.BoundingBox(shape)
        cut_box = geompy.MakeBox(
            Xmin - 1,
            height,
            Zmin - 1,
            Xmax + 1,
            Ymax + 1,
            Zmax + 1,
        )
    elif height_axis == 2:
        [Xmin, Xmax, Ymin, Ymax, Zmin, Zmax] = geompy.BoundingBox(shape)
        cut_box = geompy.MakeBox(
            Xmin - 1,
            Ymin - 1,
            height,
            Xmax + 1,
            Ymax + 1,
            Zmax + 1,
        )
    else:
        raise ValueError("height_axis must be 0, 1, or 2")

    return geompy.MakeCut(shape, cut_box)


def makeCylinder(radius, height, geompy, center_height=0, seam=None, theName=None):
    O = geompy.MakeVertex(0, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    cylinder = geompy.MakeCylinder(O, OY, radius, height)
    if seam:
        cylinder = rotateToSeam(cylinder, seam, height, radius, geompy)
    if center_height > 0:
        cylinder = geompy.MakeTranslation(cylinder, 0, center_height - height / 2, 0)

    if theName:
        geompy.addToStudy(cylinder, theName)
    return cylinder


def getNearestPoint(shape, point, geompy):
    return geompy.GetShapesNearPoint(
        shape,
        point,
        geompy.ShapeType["VERTEX"],
    )


def rotateToSeam(base_shape, intersect_shape, height, radius, geompy):
    shape_intersect = geompy.MakeSection(intersect_shape, base_shape, True)
    v_seam = geompy.MakeVertex(0, height, radius)
    vs_shape = getNearestPoint(shape_intersect, v_seam, geompy)
    v_shape = geompy.SubShapeAllSortedCentres(vs_shape, geompy.ShapeType["VERTEX"])[0]
    center = geompy.MakeVertex(0, height, 0)
    return geompy.MakeRotationThreePoints(base_shape, center, v_seam, v_shape)


def getEdgeInShape(edge, shape, geompy):
    points = geompy.SubShapeAllSortedCentres(edge, geompy.ShapeType["VERTEX"])
    try:
        return geompy.GetEdge(shape, points[0], points[1])
    except RuntimeError:
        geompy.addToStudy(edge, f"failed_edge")
        return None


def pointInRadius(x, y, R, r=0):
    point_r = math.sqrt(x**2 + y**2)
    return point_r >= r and point_r <= R


def addCorrespondingFacesToGroup(shape, faces, group, geompy):
    """
    Find faces in shape corresponding to each face in faces,
    and add them to group.
    """
    failed = 0
    for face in faces:
        edges = geompy.SubShapeAll(face, geompy.ShapeType["EDGE"])
        try:
            shape_face = geompy.GetFaceByEdges(shape, edges[0], edges[1])
            geompy.UnionList(group, [shape_face])
        except RuntimeError:
            failed += 1
            geompy.addToStudy(face, f"failed_face{failed}")


def getBoundingY(shape, geompy):
    if not shape:
        return None, None
    [_, _, y_min, y_max, _, _] = geompy.BoundingBox(shape)
    return y_min, y_max


def getBoundingX(shape, geompy):
    if not shape:
        return None, None
    [x_min, x_max, _, _, _, _] = geompy.BoundingBox(shape)
    return x_min, x_max


def getCylinderOuterEdges(cylinder, radius, num_partitions, geompy, height=0):
    angle = 2 * math.pi / num_partitions
    offset = angle / 2
    edges = []
    for theta in [n * angle for n in range(num_partitions)]:
        vertex = geompy.MakeVertex(
            radius * math.cos(theta + offset), height, radius * math.sin(theta + offset)
        )
        edges.append(geompy.GetEdgeNearPoint(cylinder, vertex))
    return edges


def getCylinderRadialEdges(
    cylinder, height, geompy, vertical_axis=None, normal=None, pt=None
):
    """
    Returns a list of edges on cylinder at distance radius in plane
    defined by normal and pt. Only edges in +x half-space.
    """
    if not normal:
        normal = geompy.MakeVectorDXDYDZ(0, 0, 1)
    else:
        normal = normalizeVector(normal, geompy)
    if not pt:
        pt = geompy.MakeVertex(0, 0, 0)
    if not vertical_axis:
        vertical_axis = geompy.MakeVectorDXDYDZ(0, 1, 0)
    else:
        vertical_axis = normalizeVector(vertical_axis, geompy)

    # edges on plane
    edges = geompy.GetShapesOnPlaneWithLocation(
        cylinder,
        geompy.ShapeType["EDGE"],
        normal,
        pt,
        GEOM.ST_ON,
    )
    edges = geompy.MakeCompound(edges, theName="edges1")
    # in +x half-space
    cross = geompy.CrossProduct(normal, vertical_axis)
    geompy.addToStudy(cross, "cross")
    edges = geompy.GetShapesOnPlaneWithLocation(
        edges,
        geompy.ShapeType["EDGE"],
        cross,
        geompy.MakeVertex(0, 0, 0),
        GEOM.ST_IN,
    )
    edges = geompy.MakeCompound(edges, theName="edges2")
    # at height
    point = geompy.MakeVertex(0, 0, 0)
    if height > 0:
        height_vector = geompy.Scale(vertical_axis, None, height)
        point = geompy.TranslateVector(point, height_vector)
    edges = geompy.GetShapesOnPlaneWithLocation(
        edges,
        geompy.ShapeType["EDGE"],
        vertical_axis,
        point,
        GEOM.ST_ON,
    )
    edges = geompy.MakeCompound(edges, theName="edges3")
    return geompy.SubShapeAllSortedCentres(edges, geompy.ShapeType["EDGE"])


def getCylinderVerticalEdges(
    cylinder, radius, geompy, vertical_axis=None, normal=None, pt=None
):
    """
    Returns a list of edges on cylinder at distance radius in plane
    defined by normal and pt. Only edges in half-space defined by cross
    product of normal and vertical_axis.
    """
    if not normal:
        normal = geompy.MakeVectorDXDYDZ(0, 0, 1)
    else:
        normal = salome_helpers.normalizeVector(normal)
    if not pt:
        pt = geompy.MakeVertex(0, 0, 0)
    if not vertical_axis:
        vertical_axis = geompy.MakeVectorDXDYDZ(0, 1, 0)
    else:
        vertical_axis = salome_helpers.normalizeVector(vertical_axis)
    # edges on plane
    edges = geompy.GetShapesOnPlaneWithLocation(
        cylinder,
        geompy.ShapeType["EDGE"],
        normal,
        pt,
        GEOM.ST_ON,
    )
    edges = geompy.MakeCompound(edges, theName="edges1")
    # in +x half-space
    cross = geompy.CrossProduct(normal, vertical_axis)
    geompy.addToStudy(cross, "cross")
    edges = geompy.GetShapesOnPlaneWithLocation(
        edges,
        geompy.ShapeType["EDGE"],
        cross,
        geompy.MakeVertex(0, 0, 0),
        GEOM.ST_IN,
    )
    edges = geompy.MakeCompound(edges, theName="edges2")
    # at distance radius
    edges = geompy.GetShapesOnCylinder(
        theShape=edges,
        theShapeType=geompy.ShapeType["EDGE"],
        theAxis=vertical_axis,
        theRadius=radius,
        theState=GEOM.ST_ON,
        theName="edges3",
    )
    edges = geompy.MakeCompound(edges, theName="edges3")
    return geompy.SubShapeAllSortedCentres(edges, geompy.ShapeType["EDGE"])


def makeGroupFromObject(shape, group_object, geompy, shapeType=None):
    if not shapeType:
        shapeType = geompy.ShapeType["SOLID"]
        group_object = geompy.MakePartition(
            [group_object],
            [shape],
            [],
            [],
            shapeType,
        )
        geompy.addToStudy(group_object, "group_object")
        object_faces = geompy.SubShapeAllSortedCentres(
            group_object, geompy.ShapeType["FACE"]
        )
        group = geompy.CreateGroup(shape, geompy.ShapeType["FACE"])
        geompy.addToStudyInFather(shape, group, "group")
        addCorrespondingFacesToGroup(shape, object_faces, group, geompy)
    return group


def pointDistance(p1, p2, geompy):
    x1, y1, z1 = geompy.PointCoordinates(p1)
    x2, y2, z2 = geompy.PointCoordinates(p2)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def edgeInsideOut(edge, geompy, center=None):
    """
    Returns true if the first point of the edge is closer to the center (default: origin)
    than the second point of the edge is.
    """
    if not center:
        center = geompy.MakeVertex(0, 0, 0)

    p1, p2 = geompy.SubShapeAll(edge, geompy.ShapeType["VERTEX"])

    if pointDistance(p1, center, geompy) < pointDistance(p2, center, geompy):
        return True

    return False


def makeWedge(radius, height, angle, geompy):
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    Face_1 = geompy.MakeFaceHW(radius, height, 1)
    Translation_1 = geompy.MakeTranslation(Face_1, radius / 2, height / 2, 0)
    wedge = geompy.MakeRevolution(Translation_1, OY, angle * math.pi / 180.0)
    geompy.addToStudy(wedge, "wedge")
    return wedge
