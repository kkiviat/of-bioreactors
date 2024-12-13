"""Helper methods to read physical properties from case files."""
import os
import subprocess


def getRhoWater(case_dir):
    file_name = os.path.join(case_dir, "constant/physicalProperties.water")
    command = (
        f"foamDictionary {file_name} -entry mixture/equationOfState/rho -value -expand"
    )
    return float(subprocess.check_output(command, shell=True, text=True))


def getMuWater(case_dir):
    file_name = os.path.join(case_dir, "constant/physicalProperties.water")
    command = f"foamDictionary {file_name} -entry mixture/transport/mu -value -expand"
    return float(subprocess.check_output(command, shell=True, text=True))


def getMuAir(case_dir):
    file_name = os.path.join(case_dir, "constant/physicalProperties.air")
    command = f"foamDictionary {file_name} -entry mixture/transport/mu -value -expand"
    return float(subprocess.check_output(command, shell=True, text=True))


def getPRef(case_dir):
    file_name = os.path.join(case_dir, "constant/phaseProperties")
    command = (
        f"foamDictionary {file_name} -entry air/isothermalCoeffs/p0 -value -expand"
    )
    return float(subprocess.check_output(command, shell=True, text=True))


def getBubbleDiameter(case_dir):
    file_name = os.path.join(case_dir, "constant/phaseProperties")
    command = (
        f"foamDictionary {file_name} -entry air/isothermalCoeffs/d0 -value -expand"
    )
    return float(subprocess.check_output(command, shell=True, text=True))
