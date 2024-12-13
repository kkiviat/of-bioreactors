"""Sets up additional parameters for the case.

This file should be executed from a case's derivedParameters.py script like

with open(os.path.join(scripts_dir, "derivedParameters.py")) as in_file:
    exec(in_file.read())

A geometry_config.GeometryConfig called geometry_config must be defined
in the case's derivedParameters.py
"""
import math
import os
import pickle

from turbulence_calculations import epsilonViscosityRatio, kInlet

config_dir = os.path.join(projectRoot, config_dir_name)
functionObjectsDir = os.path.join(projectRoot, functionObjects_dir_name)

## geometry
with open("geometry.pkl", "wb") as f:
    pickle.dump(geometry_config, f)

tank_diameter = geometry_config.tank.tank_diameter
tank_height = geometry_config.tank.tank_height
sparger_height = geometry_config.sparger.top()
sparger_bottom = geometry_config.sparger.bottom()
impeller_height = geometry_config.impeller_heights()[0]
impeller_heights = geometry_config.impeller_heights()
impeller_shaft_bottom = tank_height - geometry_config.impeller_shaft.shaft_length
impeller_shaft_radius = geometry_config.impeller_shaft.shaft_diameter / 2

fill_height = fill_amount * tank_height

MRF_radius = geometry_config.MRF_config.radius
MRF_bottom = geometry_config.MRF_config.bottom
MRF_top = geometry_config.MRF_config.top

impeller_refinement_height = min(impeller_heights) - MRF_bottom

## agitation rate
omega = 2 * math.pi * RPM / 60


## Probe locations
probe_r = tank_diameter * 0.5 * 0.7
probe_x = probe_r * math.cos(math.pi / 4)
probe_z = probe_r * math.sin(math.pi / 4)
probe_y_bottom = sparger_height
probe_y_mid1 = impeller_height
probe_y_top = tank_height * 0.9
probe_y_mid2 = (probe_y_top + impeller_height) / 2

## sparger

# set flow rate to get superficial gas velocity v_s at sparger height
volumetric_flow = v_s * math.pi * tank_diameter**2 / 4

Area_sparger = math.pi * (
    geometry_config.sparger.outer_radius() ** 2
    - geometry_config.sparger.inner_radius() ** 2
)
Area_holes = Area_sparger * sparger_inlet_fraction
alpha_air_in = sparger_inlet_fraction
U_in = volumetric_flow / Area_holes

# set reference pressure for bubble diameter to atmospheric
p_ref_bubble = 1e5

## turbulence
k_in = kInlet(U_in, turbulence_intensity)
eps_in = epsilonViscosityRatio(
    k=k_in, viscosity_ratio=viscosity_ratio, rho=993, mu=7e-4
)
omega_in = eps_in / k_in

k_out = kInlet(v_s, turbulence_intensity)
eps_out = epsilonViscosityRatio(
    k=k_out, viscosity_ratio=viscosity_ratio, rho=993, mu=7e-4
)
omega_out = eps_out / k_out
