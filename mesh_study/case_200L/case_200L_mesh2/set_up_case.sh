python3 /data/openfoam-10/run/of-bioreactors/scripts/write_params.py "/data/openfoam-10/run/of-bioreactors/mesh_study/case_200L/case_200L_mesh2"
pyFoamPrepareCase.py --no-mesh-create --values-string="{'num_processors':$1}" .
decomposePar -force
