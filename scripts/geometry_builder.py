"""Methods to construct a GeometryConfig defining bioreactors."""
from collections import namedtuple

import geometry_config

Dimensions = namedtuple(
    "dimensions",
    [
        "tank_diameter",
        "tank_height",
        "tank_bottom_radius",
        "thickness",
        "rushton_diameter",
        "rushton_disk_diameter",
        "rushton_blade_height",
        "rushton_blade_width",
        "pitched_blade_corner_to_corner",
        "pitched_blade_center_to_line",
        "pitched_blade_center_to_edge",
        "pitched_connector_diameter",
        "pitched_connector_height",
        "impeller_refinement_height",
        "impeller_shaft_diameter",
        "impeller_shaft_length",
        "impeller_shaft_bottom_attached",
        "sparger_diameter",
        "sparger_tube_diameter",
        "sparger_top_height",
        "baffle_width",
        "baffle_gap",
        "baffle_height",
        "num_baffles",
        "MRF_radius",
    ],
)


def _getDimensions(V):
    """Constructs default dimensions for a bioreactor with volume V."""
    scaling_factor = (V / 2.5) ** (1 / 3)  # relative to 2.5 m^3 case
    tank_diameter = 1.168 * scaling_factor
    tank_height = 2 * tank_diameter
    tank_bottom_radius = tank_diameter / 4
    fill_height = tank_diameter * 1.6
    thickness = tank_diameter / 120
    rushton_diameter = 0.4 * tank_diameter
    rushton_disk_diameter = 0.85 * rushton_diameter
    rushton_blade_height = 0.2 * rushton_diameter
    rushton_blade_width = 0.25 * rushton_diameter
    pitched_diameter = 0.4 * tank_diameter
    pitched_blade_corner_to_corner = 0.68 * pitched_diameter
    pitched_blade_center_to_line = 0.15 * pitched_diameter
    pitched_blade_center_to_edge = 0.35 * pitched_diameter
    pitched_connector_diameter = (
        pitched_diameter / 2 - pitched_blade_center_to_edge
    ) * 2
    pitched_connector_height = 0.8 * pitched_connector_diameter
    impeller_refinement_height = 0.7 * rushton_diameter
    impeller_shaft_diameter = 0.05 * tank_diameter
    impeller_shaft_length = tank_height - rushton_diameter
    sparger_diameter = 0.85 * rushton_diameter
    sparger_tube_diameter = 0.08 * sparger_diameter
    sparger_top_height = 0.5 * rushton_diameter
    baffle_width = tank_diameter / 12
    baffle_gap = tank_diameter / 60
    baffle_height = tank_height - sparger_top_height
    num_baffles = 4
    MRF_radius = 0.3 * tank_diameter

    dimensions = Dimensions(
        tank_diameter=tank_diameter,
        tank_height=tank_height,
        tank_bottom_radius=tank_bottom_radius,
        thickness=thickness,
        rushton_diameter=rushton_diameter,
        rushton_disk_diameter=rushton_disk_diameter,
        rushton_blade_height=rushton_blade_height,
        rushton_blade_width=rushton_blade_width,
        pitched_blade_corner_to_corner=pitched_blade_corner_to_corner,
        pitched_blade_center_to_line=pitched_blade_center_to_line,
        pitched_blade_center_to_edge=pitched_blade_center_to_edge,
        pitched_connector_diameter=pitched_connector_diameter,
        pitched_connector_height=pitched_connector_height,
        impeller_refinement_height=impeller_refinement_height,
        impeller_shaft_diameter=impeller_shaft_diameter,
        impeller_shaft_length=impeller_shaft_length,
        sparger_diameter=sparger_diameter,
        sparger_tube_diameter=sparger_tube_diameter,
        sparger_top_height=sparger_top_height,
        baffle_width=baffle_width,
        baffle_gap=baffle_gap,
        baffle_height=baffle_height,
        num_baffles=num_baffles,
        MRF_radius=MRF_radius,
        impeller_shaft_bottom_attached=False,
    )
    return dimensions


def _getDimensions_villiger_5000L():
    """
    Custom dimensions based on the 5000 L bioreactor from

    Villiger, Neunstoecklin & Karst et al. (2018) Experimental and
    CFD Physical Characterization of Animal Cell Bioreactors: From
    Micro- to Production Scale, Biochemical Engineering Journal.
    """
    tank_diameter = 1.7
    tank_height = 2.4 / 0.8
    tank_bottom_radius = tank_diameter / 4
    fill_height = 2.4
    thickness = tank_diameter / 120
    rushton_diameter = 0.5
    rushton_disk_diameter = 0.85 * rushton_diameter
    rushton_blade_height = 0.2 * rushton_diameter
    rushton_blade_width = 0.25 * rushton_diameter
    pitched_diameter = 0.7
    pitched_blade_corner_to_corner = 0.68 * pitched_diameter
    pitched_blade_center_to_line = 0.15 * pitched_diameter
    pitched_blade_center_to_edge = 0.35 * pitched_diameter
    pitched_connector_diameter = (
        pitched_diameter / 2 - pitched_blade_center_to_edge
    ) * 2
    pitched_connector_height = 0.8 * pitched_connector_diameter
    impeller_refinement_height = 0.7 * rushton_diameter
    impeller_shaft_diameter = 0.04 * tank_diameter
    top_impeller = 0.4 + 0.7
    impeller_shaft_length = 1.64
    sparger_diameter = rushton_diameter
    sparger_tube_diameter = 0.08 * sparger_diameter
    sparger_top_height = 0.2
    baffle_width = 0.175
    baffle_gap = 0.02
    baffle_height = tank_height - 0.38
    num_baffles = 3
    MRF_radius = 0.3 * tank_diameter

    dimensions = Dimensions(
        tank_diameter=tank_diameter,
        tank_height=tank_height,
        tank_bottom_radius=tank_bottom_radius,
        thickness=thickness,
        rushton_diameter=rushton_diameter,
        rushton_disk_diameter=rushton_disk_diameter,
        rushton_blade_height=rushton_blade_height,
        rushton_blade_width=rushton_blade_width,
        pitched_blade_corner_to_corner=pitched_blade_corner_to_corner,
        pitched_blade_center_to_line=pitched_blade_center_to_line,
        pitched_blade_center_to_edge=pitched_blade_center_to_edge,
        pitched_connector_diameter=pitched_connector_diameter,
        pitched_connector_height=pitched_connector_height,
        impeller_refinement_height=impeller_refinement_height,
        impeller_shaft_diameter=impeller_shaft_diameter,
        impeller_shaft_length=impeller_shaft_length,
        sparger_diameter=sparger_diameter,
        sparger_tube_diameter=sparger_tube_diameter,
        sparger_top_height=sparger_top_height,
        baffle_width=baffle_width,
        baffle_gap=baffle_gap,
        baffle_height=baffle_height,
        num_baffles=num_baffles,
        MRF_radius=MRF_radius,
        impeller_shaft_bottom_attached=True,
    )
    return dimensions


def _makeBaseGeometry(dims):
    """
    Constructs a base GeometryConfig without any impeller configuration.
    """
    config = geometry_config.GeometryConfig(
        tank=geometry_config.TankConfig(
            tank_diameter=dims.tank_diameter,
            tank_height=dims.tank_height,
            tank_bottom_radius=dims.tank_bottom_radius,
        ),
        sparger=geometry_config.RingSpargerConfig(
            diameter=dims.sparger_diameter,
            tube_diameter=dims.sparger_tube_diameter,
            height=dims.sparger_top_height,
        ),
        impeller_shaft=geometry_config.ImpellerShaftConfig(
            shaft_diameter=dims.impeller_shaft_diameter,
            shaft_length=dims.impeller_shaft_length,
            bottom_attached=dims.impeller_shaft_bottom_attached,
        ),
        baffles=geometry_config.BafflesConfig(
            baffle_width=dims.baffle_width,
            baffle_height=dims.baffle_height,
            gap_width=dims.baffle_gap,
            num_baffles=dims.num_baffles,
            thickness=dims.thickness,
        ),
    )

    return config


def makeGeometry_villiger_5000L():
    """
    Makes a GeometryConfig for the 5000 L bioreactor from
    Villiger et al. 2018.
    """
    dims = _getDimensions_villiger_5000L()
    base_config = _makeBaseGeometry(dims)

    bottom_impeller_height = 0.4
    impeller_spacing = 0.7
    top_impeller_height = bottom_impeller_height + impeller_spacing

    config = geometry_config.GeometryConfig(
        tank=base_config.tank,
        sparger=base_config.sparger,
        impeller_shaft=base_config.impeller_shaft,
        baffles=base_config.baffles,
        MRF_config=geometry_config.MRFConfig(
            radius=dims.MRF_radius,
            bottom=0.25,
            top=top_impeller_height + dims.impeller_refinement_height / 2,
        ),
        rushton_impeller=geometry_config.RushtonConfig(
            disk_diameter=dims.rushton_disk_diameter,
            blade_height=dims.rushton_blade_height,
            blade_width=dims.rushton_blade_width,
            radius=dims.rushton_diameter / 2,
            disk_thickness=dims.thickness,
            blade_thickness=dims.thickness,
        ),
        rushton_impeller_heights=[bottom_impeller_height],
        pitched_impeller=geometry_config.PitchedBladeConfig(
            blade_corner_to_corner=dims.pitched_blade_corner_to_corner,
            blade_center_to_corner_to_corner_line=dims.pitched_blade_center_to_line,
            blade_center_to_edge=dims.pitched_blade_center_to_edge,
            connector_diameter=dims.pitched_connector_diameter,
            connector_height=dims.pitched_connector_height,
            thickness=dims.thickness,
        ),
        pitched_impeller_heights=[bottom_impeller_height + impeller_spacing],
    )

    return config


def makeTwoRushtonGeometry(V):
    """
    Constructs a GeometryConfig for a bioreactor with two Rushton impellers.
    """
    dims = _getDimensions(V)
    base_config = _makeBaseGeometry(dims)

    bottom_impeller_height = dims.rushton_diameter
    impeller_spacing = 1.5 * dims.rushton_diameter
    top_impeller_height = bottom_impeller_height + impeller_spacing

    config = geometry_config.GeometryConfig(
        tank=base_config.tank,
        sparger=base_config.sparger,
        impeller_shaft=base_config.impeller_shaft,
        baffles=base_config.baffles,
        MRF_config=geometry_config.MRFConfig(
            radius=dims.MRF_radius,
            bottom=bottom_impeller_height - dims.impeller_refinement_height / 2,
            top=top_impeller_height + dims.impeller_refinement_height / 2,
        ),
        rushton_impeller=geometry_config.RushtonConfig(
            disk_diameter=dims.rushton_disk_diameter,
            blade_height=dims.rushton_blade_height,
            blade_width=dims.rushton_blade_width,
            radius=dims.rushton_diameter / 2,
            disk_thickness=dims.thickness,
            blade_thickness=dims.thickness,
        ),
        rushton_impeller_heights=[
            bottom_impeller_height,
            bottom_impeller_height + impeller_spacing,
        ],
    )

    return config


def makeTwoPitchedBladeGeometry(V):
    """
    Constructs a GeometryConfig for a bioreactor with two pitched impellers.
    """
    dims = _getDimensions(V)
    base_config = _makeBaseGeometry(dims)

    bottom_impeller_height = dims.rushton_diameter
    impeller_spacing = 1.5 * dims.rushton_diameter
    top_impeller_height = bottom_impeller_height + impeller_spacing

    config = geometry_config.GeometryConfig(
        tank=base_config.tank,
        sparger=base_config.sparger,
        impeller_shaft=base_config.impeller_shaft,
        baffles=base_config.baffles,
        MRF_config=geometry_config.MRFConfig(
            radius=dims.MRF_radius,
            bottom=bottom_impeller_height - dims.impeller_refinement_height / 2,
            top=top_impeller_height + dims.impeller_refinement_height / 2,
        ),
        pitched_impeller=geometry_config.PitchedBladeConfig(
            blade_corner_to_corner=dims.pitched_blade_corner_to_corner,
            blade_center_to_corner_to_corner_line=dims.pitched_blade_center_to_line,
            blade_center_to_edge=dims.pitched_blade_center_to_edge,
            connector_diameter=dims.pitched_connector_diameter,
            connector_height=dims.pitched_connector_height,
            thickness=dims.thickness,
        ),
        pitched_impeller_heights=[
            bottom_impeller_height,
            bottom_impeller_height + impeller_spacing,
        ],
    )

    return config


def makeRushtonPitchedBladeGeometry(V):
    """
    Constructs a GeometryConfig for a bioreactor with one Rushton
    impeller and one pitched impeller.
    """
    dims = _getDimensions(V)
    base_config = _makeBaseGeometry(dims)

    bottom_impeller_height = dims.rushton_diameter
    impeller_spacing = 1.5 * dims.rushton_diameter
    top_impeller_height = bottom_impeller_height + impeller_spacing

    config = geometry_config.GeometryConfig(
        tank=base_config.tank,
        sparger=base_config.sparger,
        impeller_shaft=base_config.impeller_shaft,
        baffles=base_config.baffles,
        MRF_config=geometry_config.MRFConfig(
            radius=dims.MRF_radius,
            bottom=bottom_impeller_height - dims.impeller_refinement_height / 2,
            top=top_impeller_height + dims.impeller_refinement_height / 2,
        ),
        rushton_impeller=geometry_config.RushtonConfig(
            disk_diameter=dims.rushton_disk_diameter,
            blade_height=dims.rushton_blade_height,
            blade_width=dims.rushton_blade_width,
            radius=dims.rushton_diameter / 2,
            disk_thickness=dims.thickness,
            blade_thickness=dims.thickness,
        ),
        rushton_impeller_heights=[bottom_impeller_height],
        pitched_impeller=geometry_config.PitchedBladeConfig(
            blade_corner_to_corner=dims.pitched_blade_corner_to_corner,
            blade_center_to_corner_to_corner_line=dims.pitched_blade_center_to_line,
            blade_center_to_edge=dims.pitched_blade_center_to_edge,
            connector_diameter=dims.pitched_connector_diameter,
            connector_height=dims.pitched_connector_height,
            thickness=dims.thickness,
        ),
        pitched_impeller_heights=[bottom_impeller_height + impeller_spacing],
    )

    return config
