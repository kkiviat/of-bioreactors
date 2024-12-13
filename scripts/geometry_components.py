import math

import salome_helpers


def make_tank(config, geompy, seam=None):
    """Makes a tank geometry from a GeometryConfig"""
    O = geompy.MakeVertex(0, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    R = config.tank_diameter / 2
    H = config.tank_height
    r = config.tank_bottom_radius
    tank = geompy.MakeCylinder(O, OY, R, H - r)
    tank = geompy.TranslateDXDYDZ(tank, 0, r, 0)
    geompy.addToStudy(tank, "tank_initial")
    [tank_shell] = geompy.ExtractShapes(tank, geompy.ShapeType["SHELL"], True)

    if config.tank_bottom_radius > 0:
        # Add the curved bottom
        Vertex_1 = geompy.MakeVertex(0, r, R - r)
        Vertex_2 = geompy.MakeVertex(0, r, R)
        Vertex_3 = geompy.MakeVertex(0, 0, R - r)
        Arc = geompy.MakeArcCenter(Vertex_1, Vertex_2, Vertex_3, False)
        revolution = geompy.MakeRevolution(Arc, OY, 360 * math.pi / 180.0)
        bottom = geompy.MakeDiskPntVecR(O, OY, R - r)
        tank = geompy.MakeFuseList([revolution, bottom, tank_shell], True, True)
        geompy.addToStudy(tank, "tank_curved")
        if seam:
            tank = salome_helpers.rotateToSeam(tank, seam, H, R, geompy)
        geompy.addToStudy(tank, "tank_curved_rotated")

        tank_faces = geompy.SubShapeAllSortedCentresIDs(tank, geompy.ShapeType["FACE"])
        tankwall = geompy.CreateGroup(tank, geompy.ShapeType["FACE"])
        geompy.addToStudyInFather(tank, tankwall, "tankwall")
        geompy.UnionIDs(tankwall, tank_faces[:2] + tank_faces[3:-1])
    else:
        if seam:
            tank = salome_helpers.rotateToSeam(tank, seam, H, R, geompy)
        tank_faces = geompy.SubShapeAllSortedCentresIDs(tank, geompy.ShapeType["FACE"])
        tankwall = geompy.CreateGroup(tank, geompy.ShapeType["FACE"])
        geompy.UnionIDs(tankwall, tank_faces[:-1])

    outlet = geompy.CreateGroup(tank, geompy.ShapeType["FACE"])
    geompy.addToStudyInFather(tank, outlet, "outlet")
    geompy.UnionIDs(outlet, [tank_faces[-1]])

    tank_solid = geompy.MakeSolid([geompy.MakeFuseList([tankwall, outlet], True, True)])
    geompy.addToStudy(tank_solid, "tank_solid")
    return tankwall, outlet, tank_solid


def make_ring_sparger(config, geompy, seam=None):
    """Takes a RingSpargerConfig as input"""
    O = geompy.MakeVertex(0, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)

    R = config.diameter / 2
    r = R - config.tube_diameter
    H = config.tube_diameter
    height = config.height

    if not config.surface_only:
        sparger_outer = geompy.MakeCylinder(O, OY, R, H)
        sparger_inner = geompy.MakeCylinder(O, OY, r, H)

        if seam:
            sparger_outer = salome_helpers.rotateToSeam(
                sparger_outer, seam, 0, R, geompy
            )
            sparger_inner = salome_helpers.rotateToSeam(
                sparger_inner, seam, 0, r, geompy
            )
        sparger = geompy.MakeCutList(sparger_outer, [sparger_inner], True)
        geompy.TranslateDXDYDZ(sparger, 0, height - H / 2, 0)
        SubFaceList = geompy.SubShapeAllSortedCentresIDs(
            sparger, geompy.ShapeType["FACE"]
        )
        sparger_upper = geompy.CreateGroup(sparger, geompy.ShapeType["FACE"])
        # last face is the top one
        geompy.UnionIDs(sparger_upper, [SubFaceList[-1]])
        sparger_lower = geompy.CreateGroup(sparger, geompy.ShapeType["FACE"])
        geompy.UnionIDs(sparger_lower, SubFaceList[:-1])
        return sparger, sparger_upper, sparger_lower

    outer_disk = geompy.MakeDiskR(R, 3)  # normal to y-axis
    inner_disk = geompy.MakeDiskR(r, 3)
    sparger_upper = geompy.MakeCut(outer_disk, inner_disk, True)
    geompy.TranslateDXDYDZ(sparger_upper, 0, height, 0)
    return None, sparger_upper, None


def make_impeller_shaft(config, tank_config, geompy, seam=None):
    """Takes a TankConfig as input"""
    O = geompy.MakeVertex(0, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    r = config.shaft_diameter / 2
    H = config.shaft_length
    top = tank_config.tank_height
    shaft = geompy.MakeCylinder(O, OY, r, H)

    if not config.bottom_attached:
        geompy.TranslateDXDYDZ(shaft, 0, top - H, 0)

    if seam:
        shaft = salome_helpers.rotateToSeam(shaft, seam, top, r, geompy)
    return shaft


def make_rushton_impeller(config, height, geompy, seam=None, cut_disk=True):
    """Takes a RushtonConfig as input"""
    O = geompy.MakeVertex(0, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
    # Make the blade wider so it can be cut down with a cylinder
    blade = geompy.MakeFaceHW(config.radius * 2.5, config.blade_height, 1)
    if config.blade_thickness > 0:
        blade = geompy.MakePrismVecH2Ways(blade, OZ, config.blade_thickness / 2)
    disk = geompy.MakeCylinder(O, OY, config.disk_diameter / 2, config.disk_thickness)
    geompy.addToStudy(disk, "disk")
    if seam:
        disk = salome_helpers.rotateToSeam(
            disk, seam, 0, config.disk_diameter / 2, geompy
        )

    blades = geompy.MultiRotate1DNbTimes(blade, OY, 6)
    geompy.TranslateDXDYDZ(blades, 0, height, 0)
    geompy.TranslateDXDYDZ(disk, 0, height - config.disk_thickness / 2, 0)

    # Cut down to correct size
    outer_cylinder = geompy.MakeCylinder(O, OY, config.radius, height * 2, 1)
    inner_cylinder = geompy.MakeCylinder(
        O, OY, config.radius - config.blade_width, height * 2, 1
    )
    blades = geompy.MakeCutList(blades, [inner_cylinder], False)
    blades = geompy.MakeCommon(blades, outer_cylinder, False)

    # Partition things to make edges line up
    if config.disk_thickness > 0:
        blades_cut = geompy.MakeCutList(blades, [disk], True)
    else:
        blades_cut = blades

    if cut_disk:
        if config.blade_thickness > 0:
            disk_cut = geompy.MakeCutList(disk, [blades], True)
        else:
            disk_cut = geompy.MakePartition(
                [disk], [blades], [], [], geompy.ShapeType["SOLID"], 0, [], 0
            )
        disk = disk_cut

    blades = blades_cut

    return blades, disk


def make_pitched_impeller(config, height, geompy, seam=None):
    O = geompy.MakeVertex(0, 0, 0)
    OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
    connector_radius = config.connector_diameter / 2
    x_corner = connector_radius + config.blade_center_to_corner_to_corner_line
    y_corner = config.blade_corner_to_corner / 2
    x_tip = connector_radius + config.blade_center_to_edge

    geomObj_1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
    sk = geompy.Sketcher2D()
    sk.addPoint(0.0, 0.0)
    sk.addSegmentAbsolute(x_corner, -y_corner)
    sk.addSegmentAbsolute(x_corner, y_corner)
    sk.addSegmentAbsolute(0.0, 0.0)
    sk.close()
    Sketch_1 = sk.wire(geomObj_1)
    triangle_face = geompy.MakeFaceWires([Sketch_1], 1)
    cut_face = geompy.MakeFaceHW(connector_radius * 0.01, connector_radius * 0.01, 1)
    triangle_face = geompy.MakeCutList(triangle_face, [cut_face], True)
    corner_1 = geompy.MakeVertex(x_corner, y_corner, 0)
    corner_2 = geompy.MakeVertex(x_corner, -y_corner, 0)
    tip_point = geompy.MakeVertex(x_tip, 0, 0)
    Arc_1 = geompy.MakeArc(corner_1, tip_point, corner_2)
    Line_1 = geompy.MakeLineTwoPnt(corner_2, corner_1)
    arc_face = geompy.MakeFaceWires([Arc_1, Line_1], 1)
    blade_face = geompy.MakeFuseList([triangle_face, arc_face], True, True)

    if config.thickness > 0:
        blade_face = geompy.MakePrismVecH2Ways(blade_face, OZ, config.thickness / 2)

    geompy.Rotate(blade_face, OX, 45 * math.pi / 180.0)
    blades = geompy.MultiRotate1DNbTimes(blade_face, OY, 3)
    connector = geompy.MakeCylinder(O, OY, connector_radius, config.connector_height)
    if seam:
        connector = salome_helpers.rotateToSeam(
            connector, seam, 0, connector_radius, geompy
        )

    geompy.TranslateDXDYDZ(blades, 0, height, 0)
    geompy.TranslateDXDYDZ(connector, 0, height - config.connector_height / 2, 0)

    # Partition things to make edges line up
    if config.thickness > 0:
        connector_cut = geompy.MakeCutList(connector, [blades], True)
        blades = geompy.MakeCutList(blades, [connector], True)
    else:
        connector_cut = geompy.MakePartition(
            [connector], [blades], [], [], geompy.ShapeType["FACE"], 0, [], 0
        )
        blades = geompy.MakePartition(
            [blades], [connector], [], [], geompy.ShapeType["FACE"], 0, [], 0
        )

    connector = connector_cut
    return blades, connector


def make_baffles(baffle_config, tank_config, geompy, tank_solid=None):
    """Takes a BafflesConfig as input"""
    O = geompy.MakeVertex(0, 0, 0)
    OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
    OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
    R = tank_config.tank_diameter / 2
    H = tank_config.tank_height

    baffle = geompy.MakeFaceHW(
        tank_config.tank_diameter, baffle_config.baffle_height, 1
    )
    if baffle_config.thickness > 0:
        baffle = geompy.MakePrismVecH2Ways(baffle, OZ, baffle_config.thickness / 2)

    geompy.TranslateDXDYDZ(
        baffle,
        0,
        H - baffle_config.baffle_height / 2,
        0,
    )

    # Cut down to correct size
    outer_cylinder = geompy.MakeCylinder(O, OY, R - baffle_config.gap_width, 2 * H)
    inner_cylinder = geompy.MakeCylinder(
        O, OY, R - baffle_config.gap_width - baffle_config.baffle_width, H
    )
    baffle = geompy.MakeCutList(baffle, [inner_cylinder], False)
    baffle = geompy.MakeCommon(baffle, outer_cylinder, False)

    # cut off the second one
    baffle = salome_helpers.shapeBelowHeight(baffle, 0, geompy, height_axis=0)

    baffles = geompy.MultiRotate1DNbTimes(baffle, OY, baffle_config.num_baffles)

    return baffles
