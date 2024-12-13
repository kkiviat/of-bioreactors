import geometry_components
import salome_helpers
import GEOM


class Sparger:
    def __init__(self, sparger_config, tank_height, geompy, seam):
        self.config = sparger_config
        self.geompy = geompy
        self.seam = seam
        self.tank_height = tank_height
        self.partitions = None
        self._build(tank_height)

    def _build(self, tank_height):
        (
            self.solid,
            self.sparger_upper,
            self.sparger_lower,
        ) = geometry_components.make_ring_sparger(
            self.config, self.geompy, seam=self.seam
        )
        if self.solid:
            self.geompy.addToStudy(self.solid, "sparger")

        self.geompy.addToStudy(self.sparger_upper, "sparger_upper")

    def getPartitions(self):
        if self.partitions:
            return self.partitions

        if self.config.surface_only:
            sparger_top = self.config.height
            sparger_bottom = sparger_top
        else:
            sparger_bottom = self.config.height - self.config.tube_diameter / 2
            sparger_top = sparger_bottom + self.config.tube_diameter

        plane_sparger_top = salome_helpers.horizontalPlane(sparger_top, self.geompy)
        plane_sparger_bottom = salome_helpers.horizontalPlane(
            sparger_bottom, self.geompy
        )

        sparger_outer_radius = self.config.diameter / 2
        sparger_inner_radius = sparger_outer_radius - self.config.tube_diameter
        sparger_inner_cylinder = salome_helpers.makeCylinder(
            sparger_inner_radius, self.tank_height, self.geompy, seam=self.seam
        )
        sparger_outer_cylinder = salome_helpers.makeCylinder(
            sparger_outer_radius, self.tank_height, self.geompy, seam=self.seam
        )

        self.partitions = [
            sparger_inner_cylinder,
            sparger_outer_cylinder,
            plane_sparger_bottom,
            plane_sparger_top,
        ]
        self.geompy.addToStudy(sparger_inner_cylinder, "sparger_inner_cylinder")
        self.geompy.addToStudy(sparger_outer_cylinder, "sparger_outer_cylinder")

        self.geompy.addToStudy(plane_sparger_top, "plane_sparger_top")
        self.geompy.addToStudy(plane_sparger_bottom, "plane_sparger_bottom")
        return self.partitions

    def getInsideEdge(self):
        if self.config.surface_only:
            return None

        edges_on_seam = self.geompy.GetShapesOnPlaneWithLocation(
            self.solid,
            self.geompy.ShapeType["EDGE"],
            self.geompy.GetNormal(self.seam),
            self.geompy.MakeCDG(self.seam),
            GEOM.ST_ON,
        )
        self.geompy.MakeCompound(edges_on_seam, theName="seam_edges")
        return edges_on_seam[1]

    def getUpperEdges(self, tank):
        sparger_part = self.geompy.MakePartition(
            [self.sparger_upper],
            [tank],
            [],
            [],
            self.geompy.ShapeType["FACE"],
        )

        edges_on_seam = self.geompy.GetShapesOnPlaneWithLocation(
            sparger_part,
            self.geompy.ShapeType["EDGE"],
            self.geompy.GetNormal(self.seam),
            self.geompy.MakeCDG(self.seam),
            GEOM.ST_ON,
        )
        self.geompy.MakeCompound(edges_on_seam, theName="upper_seam_edges")
        return edges_on_seam

    def createGroups(self, tank):
        if self.config.surface_only:
            raise ValueError(
                "Creating sparger groups not supported for surface_only mode"
            )

        # Sparger upper
        sparger_top = self.config.height + self.config.tube_diameter / 2
        sparger_part = self.geompy.MakePartition(
            [self.solid],
            [tank],
            [],
            [],
            self.geompy.ShapeType["SOLID"],
        )
        self.geompy.addToStudy(sparger_part, "sparger_part")
        sparger_upper_faces = self.geompy.GetShapesOnPlaneWithLocation(
            sparger_part,
            self.geompy.ShapeType["FACE"],
            self.geompy.MakeVectorDXDYDZ(0, 1, 0),
            self.geompy.MakeVertex(0, sparger_top, 0),
            GEOM.ST_ON,
        )
        sparger_upper_group = self.geompy.CreateGroup(
            tank, self.geompy.ShapeType["FACE"]
        )
        self.geompy.addToStudyInFather(tank, sparger_upper_group, "sparger_upper_group")
        salome_helpers.addCorrespondingFacesToGroup(
            tank, sparger_upper_faces, sparger_upper_group, self.geompy
        )

        # Sparger lower
        sparger_part = self.geompy.RemoveInternalFaces(sparger_part)
        [sparger_shell] = self.geompy.ExtractShapes(
            sparger_part, self.geompy.ShapeType["SHELL"], True
        )
        sparger_lower = self.geompy.MakeCutList(
            sparger_shell,
            [salome_helpers.horizontalPlane(sparger_top, self.geompy)],
            True,
        )
        sparger_lower_faces = self.geompy.SubShapeAllSortedCentres(
            sparger_lower, self.geompy.ShapeType["FACE"]
        )
        sparger_lower_group = self.geompy.CreateGroup(
            tank, self.geompy.ShapeType["FACE"]
        )
        self.geompy.addToStudyInFather(tank, sparger_lower_group, "sparger_lower_group")
        salome_helpers.addCorrespondingFacesToGroup(
            tank, sparger_lower_faces, sparger_lower_group, self.geompy
        )
        return sparger_upper_group, sparger_lower_group
