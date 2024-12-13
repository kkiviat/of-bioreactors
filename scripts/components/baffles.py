import geometry_components
import salome_helpers


class Baffles:
    def __init__(self, baffle_config, tank_config, geompy, seam):
        self.baffle_config = baffle_config
        self.tank_config = tank_config
        self.geompy = geompy
        self.seam = seam
        self.partitions = None
        self.baffles = geometry_components.make_baffles(
            self.baffle_config, self.tank_config, self.geompy
        )

    def getPartitions(self):
        if self.partitions:
            return self.partitions

        OY = self.geompy.MakeVectorDXDYDZ(0, 1, 0)
        baffle_outer_radius = (
            self.tank_config.tank_diameter / 2 - self.baffle_config.gap_width
        )
        baffle_inner_radius = baffle_outer_radius - self.baffle_config.baffle_width
        self.partitions = []
        self.partitions.append(
            salome_helpers.makeCylinder(
                baffle_inner_radius,
                self.tank_config.tank_height,
                self.geompy,
                seam=self.seam,
            )
        )
        if self.baffle_config.gap_width > 0:
            self.partitions.append(
                salome_helpers.makeCylinder(
                    baffle_outer_radius,
                    self.tank_config.tank_height,
                    self.geompy,
                    seam=self.seam,
                )
            )

        self.partitions.append(
            salome_helpers.horizontalPlane(
                self.tank_config.tank_height - self.baffle_config.baffle_height,
                self.geompy,
            )
        )

        baffle_thickness = self.baffle_config.thickness
        if baffle_thickness > 0:
            baffle_box = self.geompy.MakeBox(
                -self.tank_config.tank_diameter * 1.1,
                0,
                -baffle_thickness / 2,
                self.tank_config.tank_diameter * 1.1,
                self.tank_config.tank_height,
                baffle_thickness / 2,
            )
            baffle_box = self.geompy.MultiRotate1DNbTimes(baffle_box, OY, 4)
            self.geompy.addToStudy(baffle_box, "baffle_box")
            self.partitions.append(baffle_box)

        return self.partitions

    def createGroup(self, tank):
        baffle_group = salome_helpers.makeGroupFromObject(tank, self.baffles, self.geompy)
        return baffle_group
