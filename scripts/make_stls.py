#!/usr/bin/env python
"""Generates a set of .stl files for a bioreactor

including tank walls, baffles, impeller, sparger.
Expects a file geometry.pkl in the case directory defining the geometry_config.
"""

import argparse
import os
import pickle
import sys

import salome

salome.salome_init()
import salome_notebook

notebook = salome_notebook.NoteBook()

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--case_dir",
    help="name of case directory where geometry is configured",
    required=True,
)
args = parser.parse_args()
case_dir = args.case_dir

output_dir = os.path.join(case_dir, "constant", "triSurface")

with open(os.path.join(case_dir, "geometry.pkl"), "rb") as f:
    geometry_config = pickle.load(f)
sys.path.append(os.path.join(case_dir, "constant"))

###
### GEOM component
###

import math

import GEOM
import SALOMEDS
from salome.geom import geomBuilder

from geometry_components import (make_baffles, make_impeller_shaft,
                                 make_pitched_impeller, make_ring_sparger,
                                 make_rushton_impeller, make_tank)

## build geometry
geompy = geomBuilder.New()

# geompy.addToStudyAuto()


def add_impellers(geometry_config, geompy):
    rushton_blades_list = []
    pitched_blades_list = []
    disks_list = []
    for height in geometry_config.rushton_impeller_heights:
        blade, disk = make_rushton_impeller(
            geometry_config.rushton_impeller, height, geompy
        )
        rushton_blades_list.append(blade)
        disks_list.append(disk)

    for pitched in geometry_config.pitched_impeller_heights:
        blade, connector = make_pitched_impeller(
            geometry_config.pitched_impeller, pitched, geompy
        )
        pitched_blades_list.append(blade)
        disks_list.append(connector)

    rushton_blades = geompy.MakeFuseList(rushton_blades_list, True, True)
    pitched_blades = geompy.MakeFuseList(pitched_blades_list, True, True)
    blades = geompy.MakeFuseList(rushton_blades_list + pitched_blades_list, True, True)
    disks = geompy.MakeFuseList(disks_list, True, True)

    return rushton_blades, pitched_blades, blades, disks


sparger_solid, sparger_upper, sparger_lower = make_ring_sparger(
    geometry_config.sparger, geompy
)
if sparger_lower:
    geompy.addToStudy(sparger_lower, "sparger_lower")
if sparger_solid:
    geompy.addToStudy(sparger_solid, "sparger_solid")

geompy.addToStudy(sparger_upper, "sparger_upper")

tankwall, outlet, tank_solid = make_tank(geometry_config.tank, geompy)
geompy.addToStudy(tank_solid, "tank_solid")

rushton_blades, pitched_blades, blades, disks = add_impellers(geometry_config, geompy)
impeller = geompy.MakeFuseList([blades, disks], True, True)
geompy.addToStudy(impeller, "impeller")

O = geompy.MakeVertex(0, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
geompy.addToStudy(O, "O")
geompy.addToStudy(OY, "OY")
baffles = None
if geometry_config.baffles:
    baffles = make_baffles(
        geometry_config.baffles, geometry_config.tank, geompy, tank_solid
    )
    # cut or partition tank with baffles
    if geometry_config.baffles.thickness > 0:
        tankwall = geompy.MakeCutList(tankwall, [baffles], False)
        outlet = geompy.MakeCutList(outlet, [baffles], False)
        # Remove top faces from baffles
        baffle_faces = geompy.SubShapeAllSortedCentresIDs(
            baffles, geompy.ShapeType["FACE"]
        )
        baffle_faces = geompy.GetShapesOnPlaneWithLocationIDs(
            baffles,
            geompy.ShapeType["FACE"],
            OY,
            geompy.MakeVertex(0, geometry_config.tank.tank_height, 0),
            GEOM.ST_ON,
        )
        baffles = geompy.SuppressFaces(baffles, baffle_faces)
    else:
        tankwall = geompy.MakePartition(
            [tankwall], [baffles], [], [], geompy.ShapeType["FACE"], 0, [], 0
        )
        outlet = geompy.MakePartition(
            [outlet], [baffles], [], [], geompy.ShapeType["FACE"], 0, [], 0
        )
    geompy.addToStudy(baffles, "baffles")

impeller_shaft = None
if geometry_config.impeller_shaft:
    impeller_shaft = make_impeller_shaft(
        geometry_config.impeller_shaft, geometry_config.tank, geompy
    )
    outlet = geompy.MakeCutList(outlet, [impeller_shaft], True)
    disks = geompy.MakeCutList(disks, [impeller_shaft], True)
    blades = geompy.MakeCutList(blades, [impeller_shaft], True)
    rushton_blades = geompy.MakeCutList(rushton_blades, [impeller_shaft], True)
    pitched_blades = geompy.MakeCutList(pitched_blades, [impeller_shaft], True)
    geompy.addToStudy(impeller_shaft, "impeller_shaft_solid")
    impeller = geompy.MakeFuseList([impeller, impeller_shaft], True, True)
    impeller_and_disk = geompy.MakeFuseList([disks, impeller_shaft], True, True)
    geompy.addToStudy(impeller, "impeller")
    # Remove top face from impeller shaft
    impeller_shaft_faces = geompy.SubShapeAllSortedCentresIDs(
        impeller_shaft, geompy.ShapeType["FACE"]
    )
    impeller_shaft = geompy.SuppressFaces(impeller_shaft, [impeller_shaft_faces[-1]])
    # cut with impeller disks
    impeller_shaft = geompy.MakeCutList(impeller_shaft, [disks], True)
    geompy.addToStudy(impeller_shaft, "impeller_shaft")

geompy.addToStudy(tankwall, "tankwall")
geompy.addToStudy(outlet, "outlet")
geompy.addToStudy(impeller_and_disk, "impeller_and_disk")
cut_list = [impeller]
if sparger_solid:
    cut_list.append(sparger_solid)

tank_cut = geompy.MakeCutList(tank_solid, cut_list, True)
geompy.addToStudy(tank_cut, "tank_cut")

# single rotating zone
MRF = geompy.MakeCylinder(
    O,
    OY,
    geometry_config.MRF_config.radius,
    geometry_config.MRF_config.top - geometry_config.MRF_config.bottom,
)
MRF = geompy.TranslateDXDYDZ(
    MRF,
    0,
    geometry_config.MRF_config.bottom,
    0,
)
shaft = geompy.MakeCutList(impeller, [MRF], True)
impeller_shaft = geompy.MakeCutList(impeller_shaft, [shaft])
impeller = geompy.MakeCutList(impeller, [shaft], True)
impeller_and_disk = geompy.MakeCutList(impeller_and_disk, [shaft], True)
MRF = geompy.MakeCutList(MRF, [impeller], True)

# Make background mesh
cylinder = geompy.MakeCylinder(
    O, OY, geometry_config.tank.tank_diameter / 2, geometry_config.tank.tank_height
)
geompy.addToStudy(cylinder, "cylinder")

###
### SMESH component
###

import SALOMEDS
import SMESH
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
local_length = geometry_config.tank.tank_diameter / 800

tankwall_1 = smesh.Mesh(tankwall, "tankwall")
Regular_1D = tankwall_1.Segment()
Local_Length_1 = Regular_1D.LocalLength(local_length, None, 1e-07)
NETGEN_2D = tankwall_1.Triangle(algo=smeshBuilder.NETGEN_2D)
NETGEN_2D_Parameters_1 = NETGEN_2D.Parameters()
NETGEN_2D_Parameters_1.SetMaxSize(50)
NETGEN_2D_Parameters_1.SetMinSize(local_length)
NETGEN_2D_Parameters_1.SetOptimize(1)
NETGEN_2D_Parameters_1.SetFineness(3)
NETGEN_2D_Parameters_1.SetChordalError(-1)
NETGEN_2D_Parameters_1.SetChordalErrorEnabled(0)
NETGEN_2D_Parameters_1.SetUseSurfaceCurvature(1)
NETGEN_2D_Parameters_1.SetQuadAllowed(0)
NETGEN_2D_Parameters_1.SetUseDelauney(0)
NETGEN_2D_Parameters_1.SetCheckChartBoundary(0)
Local_Length_1.SetPrecision(1e-07)


def meshPartAndExport(part, name, local_length_hypoth, netgen_params, output_dir):
    mesh = smesh.Mesh(part, name)
    mesh.AddHypothesis(local_length_hypoth)
    mesh.Segment()
    mesh.AddHypothesis(netgen_params)
    mesh.Triangle(algo=smeshBuilder.NETGEN_2D)
    mesh.Compute()
    output_path = os.path.join(output_dir, name + ".stl")
    try:
        mesh.ExportSTL(output_path, 1)
        pass
    except:
        print("ExportSTL() failed. Invalid file name?")

    smesh.SetName(mesh.GetMesh(), name)


meshPartAndExport(MRF, "MRF", Local_Length_1, NETGEN_2D_Parameters_1, output_dir)

meshPartAndExport(
    tankwall, "tankwall", Local_Length_1, NETGEN_2D_Parameters_1, output_dir
)
meshPartAndExport(blades, "blades", Local_Length_1, NETGEN_2D_Parameters_1, output_dir)
meshPartAndExport(
    rushton_blades, "rushton_blades", Local_Length_1, NETGEN_2D_Parameters_1, output_dir
)
meshPartAndExport(
    pitched_blades, "pitched_blades", Local_Length_1, NETGEN_2D_Parameters_1, output_dir
)
meshPartAndExport(disks, "disk", Local_Length_1, NETGEN_2D_Parameters_1, output_dir)
if baffles:
    meshPartAndExport(
        baffles, "baffles", Local_Length_1, NETGEN_2D_Parameters_1, output_dir
    )

meshPartAndExport(outlet, "outlet", Local_Length_1, NETGEN_2D_Parameters_1, output_dir)
meshPartAndExport(
    sparger_upper, "sparger_upper", Local_Length_1, NETGEN_2D_Parameters_1, output_dir
)
if sparger_lower:
    meshPartAndExport(
        sparger_lower,
        "sparger_lower",
        Local_Length_1,
        NETGEN_2D_Parameters_1,
        output_dir,
    )

meshPartAndExport(shaft, "shaft", Local_Length_1, NETGEN_2D_Parameters_1, output_dir)
meshPartAndExport(
    impeller_shaft, "impeller_shaft", Local_Length_1, NETGEN_2D_Parameters_1, output_dir
)
meshPartAndExport(
    impeller_and_disk,
    "impeller_and_disk",
    Local_Length_1,
    NETGEN_2D_Parameters_1,
    output_dir,
)

## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), "Regular_1D")
smesh.SetName(NETGEN_2D.GetAlgorithm(), "NETGEN 2D")
smesh.SetName(Local_Length_1, "Local Length_1")
smesh.SetName(NETGEN_2D_Parameters_1, "NETGEN 2D Parameters_1")
smesh.SetName(tankwall_1.GetMesh(), "tankwall")


if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
