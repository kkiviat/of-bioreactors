"""Defines a GeometryConfig describing a bioreactor's dimensions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RushtonConfig:
    disk_diameter: float
    blade_height: float
    blade_width: float
    radius: float
    num_blades: int = 6
    disk_thickness: float = 0
    blade_thickness: float = 0

    def diameter(self) -> float:
        return self.radius * 2


@dataclass
class PitchedBladeConfig:
    blade_corner_to_corner: float
    blade_center_to_corner_to_corner_line: float
    blade_center_to_edge: float
    connector_diameter: float
    connector_height: float

    blade_angle: float = -45
    num_blades: int = 3
    thickness: float = 0

    def diameter(self) -> float:
        return self.radius * 2


@dataclass
class RingSpargerConfig:
    diameter: float
    tube_diameter: float
    height: float
    surface_only: bool = False  # whether to only model the inlet surface

    # not used currently
    orifice_diameter: float = 0.0016

    def top(self) -> float:
        return self.height + self.tube_diameter / 2

    def bottom(self) -> float:
        return self.height - self.tube_diameter / 2

    def outer_radius(self) -> float:
        return self.diameter / 2

    def inner_radius(self) -> float:
        return self.diameter / 2 - self.tube_diameter


@dataclass
class TankConfig:
    tank_diameter: float
    tank_height: float

    # radius of curve at bottom of tank (0 => flat bottom), not used currently
    tank_bottom_radius: float = 0


@dataclass
class ImpellerShaftConfig:
    shaft_diameter: float
    shaft_length: float

    bottom_attached: bool = False


@dataclass
class BafflesConfig:
    baffle_width: float
    baffle_height: float
    num_baffles: int
    thickness: float = 0.0
    gap_width: float = 0.0


@dataclass
class MRFConfig:
    radius: float
    bottom: float
    top: float


@dataclass
class GeometryConfig:
    sparger: RingSpargerConfig
    tank: TankConfig

    impeller_shaft: ImpellerShaftConfig

    baffles: Optional[BafflesConfig] = None

    MRF_config: Optional[MRFConfig] = None

    rushton_impeller: Optional[RushtonConfig] = None
    rushton_impeller_heights: List[float] = field(default_factory=lambda: [])

    pitched_impeller: Optional[PitchedBladeConfig] = None
    pitched_impeller_heights: List[float] = field(default_factory=lambda: [])

    def impeller_heights(self) -> List[float]:
        return sorted(self.rushton_impeller_heights + self.pitched_impeller_heights)
