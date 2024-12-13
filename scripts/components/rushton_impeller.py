import geometry_components
import salome_helpers
import math
import GEOM


class RushtonImpeller:
    def __init__(self, config, geompy, seam, cut_disk=True):
        self.config = config
        self.geompy = geompy
        self.seam = seam
        self.height = config.tank.tank_height
        self.tank_diameter = config.tank.tank_diameter
        self.impeller_list = []
        self.partitions = None
        self.cut_disk = cut_disk
        self._build()

    def splitByMRFZones(self, MRF_cylinders):
        self.impeller_list = []
        for i, MRF in enumerate(MRF_cylinders):
            new_impeller = self.geompy.MakeCommonList([MRF, self.solid], True)
            self.geompy.addToStudy(new_impeller, f"impeller_{i}")
            self.impeller_list.append(new_impeller)

        self.shaft = self.geompy.MakeCutList(self.solid, MRF_cylinders, True)
        self.geompy.addToStudy(self.shaft, "shaft")

    def createGroups(self, tank):
        if not self.impeller_list:
            raise NotImplementedError(
                "Currently only supports impellers partitioned by MRF group(s)"
            )

        impeller_groups = []
        for impeller in self.impeller_list:
            impeller_part = self.geompy.MakePartition(
                [impeller],
                [tank],
                [],
                [],
                self.geompy.ShapeType["SOLID"],
            )
            self.geompy.addToStudy(impeller_part, "impeller_part")
            impeller_faces = self.geompy.SubShapeAllSortedCentres(
                impeller_part, self.geompy.ShapeType["FACE"]
            )
            impeller_group = self.geompy.CreateGroup(
                tank, self.geompy.ShapeType["FACE"]
            )
            self.geompy.addToStudyInFather(tank, impeller_group, "impeller_group")
            salome_helpers.addCorrespondingFacesToGroup(
                tank, impeller_faces, impeller_group, self.geompy
            )
            impeller_groups.append(impeller_group)

        shaft_group = salome_helpers.makeGroupFromObject(tank, self.shaft, self.geompy)
        return impeller_groups, shaft_group

    def _build(self):
        self.blades_list = []
        disk_list = []
        disk_thickness = self.config.rushton_impeller.disk_thickness
        disk_bottom = (
            min(self.config.rushton_impeller_heights)
            - self.config.rushton_impeller.disk_thickness / 2
        )
        for height in self.config.rushton_impeller_heights:
            blades, disk = geometry_components.make_rushton_impeller(
                self.config.rushton_impeller,
                height,
                self.geompy,
                seam=self.seam,
                cut_disk=self.cut_disk,
            )
            self.blades_list.append(blades)
            disk_list.append(disk)

        self.blades = self.geompy.MakeCompound(self.blades_list, theName="blades")

        disks = self.geompy.MakeFuseList(disk_list, theName="disks")
        shaft_length = self.height - disk_bottom - disk_thickness
        shaft = salome_helpers.makeCylinder(
            self.config.impeller_shaft.shaft_diameter / 2,
            shaft_length,
            self.geompy,
            seam=self.seam,
        )
        shaft = self.geompy.MakeTranslation(
            shaft, 0, self.height - shaft_length, 0, theName="impeller_shaft"
        )
        solid_list = [shaft, disks]
        if self.config.rushton_impeller.blade_thickness > 0:
            solid_list.append(self.blades)
        self.solid = self.geompy.MakeFuseList(solid_list, theName="impeller")

    def getPartitions(self, mesh_config):
        if self.partitions:
            return self.partitions

        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        blade_height = self.config.rushton_impeller.blade_height
        disk_thickness = self.config.rushton_impeller.disk_thickness
        blade_thickness = self.config.rushton_impeller.blade_thickness
        blade_outer_radius = self.config.rushton_impeller.radius
        blade_inner_radius = (
            blade_outer_radius - self.config.rushton_impeller.blade_width
        )
        # cylinders around inside and outside blade edges
        blade_outer_cylinder = salome_helpers.makeCylinder(
            blade_outer_radius,
            self.height,
            self.geompy,
            seam=self.seam,
            theName="blade_outer_cylinder",
        )
        blade_inner_cylinder = salome_helpers.makeCylinder(
            blade_inner_radius,
            self.height,
            self.geompy,
            seam=self.seam,
            theName="blade_inner_cylinder",
        )
        blade_partitions = [blade_outer_cylinder, blade_inner_cylinder]

        # cylinder around outside edge of disk
        disk_partitions = [
            salome_helpers.makeCylinder(
                self.config.rushton_impeller.disk_diameter / 2,
                self.height,
                self.geompy,
                seam=self.seam,
            )
        ]
        # planes at top and bottom of each disk
        for height in self.config.rushton_impeller_heights:
            disk_partitions.append(
                salome_helpers.horizontalPlane(height - disk_thickness / 2, self.geompy)
            )
            disk_partitions.append(
                salome_helpers.horizontalPlane(height + disk_thickness / 2, self.geompy)
            )
            blade_partitions.append(
                salome_helpers.horizontalPlane(height - blade_height / 2, self.geompy)
            )
            blade_partitions.append(
                salome_helpers.horizontalPlane(height + blade_height / 2, self.geompy)
            )

        self.partitions = disk_partitions + blade_partitions

        # add partitions for the blade faces
        if blade_thickness > 0:
            # box around the blades themselves
            blade_box = self.geompy.MakeBox(
                -self.tank_diameter * 1.1,
                0,
                -blade_thickness / 2,
                self.tank_diameter * 1.1,
                self.height,
                blade_thickness / 2,
            )
            blade_top = self.config.rushton_impeller_heights[0] + blade_height / 2
            blade_box = self.geompy.MultiRotate1DNbTimes(blade_box, OY, 6)

            # cut with a cylinder to match the curved blade edges
            blade_box = self.geompy.MakeCommonList([blade_box, blade_outer_cylinder])

            self.geompy.addToStudy(blade_box, "blade_box")

            # add a hexagon in the center for the blade planes to converge on
            hex = salome_helpers.makeHexagon(blade_thickness, self.geompy)
            hex = self.geompy.MakeRotation(hex, OY, -math.pi / 6)
            hex = self.geompy.MakePrismDXDYDZ(
                hex, 0, min(self.config.rushton_impeller_heights), 0
            )
            self.geompy.addToStudy(hex, "hex")
            blade_box = self.geompy.MakeCutList(blade_box, [hex])
            self.partitions.append(blade_box)

            # angle the partitions outward once we're past the blades
            # blade edges are slightly curved
            blade_corner1 = salome_helpers.getNearestPoint(
                self.blades,
                self.geompy.MakeVertex(
                    blade_outer_radius, blade_top, blade_thickness / 2
                ),
                self.geompy,
            )
            blade_corner2 = salome_helpers.getNearestPoint(
                self.blades,
                self.geompy.MakeVertex(
                    blade_outer_radius, blade_top, -blade_thickness / 2
                ),
                self.geompy,
            )

            length = mesh_config.default_spacing / 2
            r = self.tank_diameter / 2 - blade_outer_radius
            theta = length / r
            outer_point1 = self.geompy.MakeTranslation(
                blade_corner1, self.tank_diameter / 2, 0, 0
            )
            outer_point2 = self.geompy.MakeTranslation(
                blade_corner2, self.tank_diameter / 2, 0, 0
            )
            outer_point1 = self.geompy.MakeRotation(outer_point1, OY, -theta)
            outer_point2 = self.geompy.MakeRotation(outer_point2, OY, theta)
            edge1 = self.geompy.MakeEdge(blade_corner1, outer_point1)
            edge2 = self.geompy.MakeEdge(blade_corner2, outer_point2)
            plane1 = self.geompy.MakePrismVecH2Ways(edge1, OY, self.height)
            plane2 = self.geompy.MakePrismVecH2Ways(edge2, OY, self.height)
            plane1 = self.geompy.MultiRotate1DNbTimes(plane1, OY, 6)
            plane2 = self.geompy.MultiRotate1DNbTimes(plane2, OY, 6)

            self.partitions += [plane1, plane2]

            self.geompy.addToStudy(plane1, "plane1")
            self.geompy.addToStudy(plane2, "plane2")

        return self.partitions

    def getBladeInsideEdges(self, tank):
        blade_height = self.config.rushton_impeller.blade_height

        blades_part = self.geompy.MakePartition(
            [self.blades],
            [tank],
            [],
            [],
            self.geompy.ShapeType["FACE"],
        )

        edges = []
        for height in self.config.rushton_impeller_heights[:-1]:
            edges += self.geompy.GetShapesOnPlaneWithLocation(
                blades_part,
                self.geompy.ShapeType["EDGE"],
                self.geompy.MakeVectorDXDYDZ(0, 1, 0),
                self.geompy.MakeVertex(0, height + blade_height / 2, 0),
                GEOM.ST_ON,
            )

        self.geompy.MakeCompound(edges, theName="impeller_edges")
        return edges

        # blade_inside_x = (
        #     self.config.rushton_impeller.radius
        #     - self.config.rushton_impeller.blade_width
        #     + eps
        # )

        # def inside(edge):
        #     [_, x_max, _, _, _, _] = self.geompy.BoundingBox(edge)
        #     return x_max <= blade_inside_x

        # inside_edges = [edge for edge in edges_on_seam if inside(edge)]
        # self.geompy.MakeCompound(edges_on_seam, theName="blade_edges")
        # self.geompy.MakeCompound(inside_edges, theName="inside_edges")
        # return inside_edges
