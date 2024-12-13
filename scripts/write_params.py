"""Writes physical parameters from case files to a parameters file."""
import sys

import dict_utils

casePath = sys.argv[1]

# read physical properties
rho_water = dict_utils.getRhoWater(casePath)
mu_water = dict_utils.getMuWater(casePath)
mu_air = dict_utils.getMuAir(casePath)
p_ref = dict_utils.getPRef(casePath)
d_ref = dict_utils.getBubbleDiameter(casePath)

with open("parameters", "w") as f:
    f.write(f"rho_water {rho_water}\n")
    f.write(f"mu_water {mu_water}\n")
    f.write(f"mu_air {mu_air}\n")
    f.write(f"p_ref {p_ref}\n")
    f.write(f"d_ref {d_ref}\n")
