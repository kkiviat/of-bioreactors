import sys
import os

projectRoot = project_root.replace('"', "")
scripts_dir = os.path.join(projectRoot, scripts_dir_name)
sys.path.append(scripts_dir)

import geometry_builder
geometry_config = geometry_builder.makeTwoRushtonGeometry(volume)

with open(os.path.join(scripts_dir, "derivedParameters.py")) as in_file:
    exec(in_file.read())
