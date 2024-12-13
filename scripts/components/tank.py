import geometry_components
import salome_helpers
import GEOM
import math

class Tank:
    def __init__(self, config, geompy, seam):
        self.config = config
        self.geompy = geompy
        self.seam = seam
        self.partitions = None
        self.radius = self.config.tank.tank_diameter / 2
        self.height = self.config.tank.tank_height
        self._build()

    def cut(self, solid, theName=None):
        self.tank = self.geompy.MakeCut(self.tank, solid, False, theName=theName)

    def partition(self, partitions, theName=None):
        self.tank = self.geompy.MakePartition(
            [self.tank],
            partitions,
            [],
            [],
            self.geompy.ShapeType["SOLID"],
            0,
            [],
            0,
            theName=theName,
        )

    def _build(self):
        O, OX, OY, OZ, OXY, OYZ, OXZ = salome_helpers.makeAxes(self.geompy)
        disk_radius = self.config.rushton_impeller.disk_diameter / 2
        blade_outer_radius = self.config.rushton_impeller.radius
        blade_inner_radius = (
            blade_outer_radius - self.config.rushton_impeller.blade_width
        )
        disk_bottom = (
            min(self.config.rushton_impeller_heights)
            - self.config.rushton_impeller.disk_thickness / 2
        )
        main_cylinder = salome_helpers.makeCylinder(
            self.radius,
            self.height,
            self.geompy,
            seam=self.seam,
            theName="main_cylinder",
        )
        self.tankwall = main_cylinder
        bottom_cylinder = self.geompy.MakeDividedCylinder(
            blade_inner_radius, disk_bottom, GEOM.HEXAGON
        )
        bottom_cylinder = self.geompy.MakeRotation(
            bottom_cylinder, OX, -math.pi / 2, theName="bottom_cylinder"
        )
        bottom_cylinder = self.geompy.MakeRotation(
            bottom_cylinder, OY, math.pi / 3, theName="bottom_cylinder"
        )
        angle_cuts = self.geompy.MultiRotate1DNbTimes(OXY, OY, 12, theName="angle_cuts")
        main_cylinder = self.geompy.MakePartition(
            [main_cylinder],
            [angle_cuts],
            [],
            [],
            self.geompy.ShapeType["SOLID"],
            0,
            [],
            0,
        )
        main_cylinder = self.geompy.MakeCutList(
            main_cylinder, [bottom_cylinder], True, theName="main_cylinder"
        )
        self.tank = self.geompy.MakeGlueFaces(
            [bottom_cylinder, main_cylinder], 1e-07, theName="tank"
        )

    def createOutletGroup(self):
        # Outlet
        outlet_faces = self.geompy.GetShapesOnPlaneWithLocation(
            self.tank,
            self.geompy.ShapeType["FACE"],
            self.geompy.MakeVectorDXDYDZ(0, 1, 0),
            self.geompy.MakeVertex(0, self.height, 0),
            GEOM.ST_ON,
        )
        outlet_group = self.geompy.CreateGroup(self.tank, self.geompy.ShapeType["FACE"])
        self.geompy.addToStudyInFather(self.tank, outlet_group, "outlet_group")
        salome_helpers.addCorrespondingFacesToGroup(
            self.tank, outlet_faces, outlet_group, self.geompy
        )
        return outlet_group

    def createWallGroup(self):
        # Walls
        bottom_faces = self.geompy.GetShapesOnPlaneWithLocation(
            self.tank,
            self.geompy.ShapeType["FACE"],
            self.geompy.MakeVectorDXDYDZ(0, 1, 0),
            self.geompy.MakeVertex(0, 0, 0),
            GEOM.ST_ON,
        )
        wall_faces = self.geompy.GetShapesOnCylinder(
            self.tank,
            self.geompy.ShapeType["FACE"],
            self.geompy.MakeVectorDXDYDZ(0, 1, 0),
            self.radius,
            GEOM.ST_ON,
        )
        wall_faces += bottom_faces
        wall_group = self.geompy.CreateGroup(self.tank, self.geompy.ShapeType["FACE"])
        self.geompy.addToStudyInFather(self.tank, wall_group, "wall_group")
        salome_helpers.addCorrespondingFacesToGroup(
            self.tank, wall_faces, wall_group, self.geompy
        )
        return wall_group
