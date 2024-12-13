"""Runs Salome with the provided script."""
import sys
from subprocess import check_call

# Build geometry in Salome
script = sys.argv[1]
args = ",".join(sys.argv[2:])
print(f"running {script} with args:")
print(args)
check_call(["/opt/SALOME/salome", "-t", "python", script, f"args:{args}"])
