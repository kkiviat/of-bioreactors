python3 /data/openfoam-10/run/of-bioreactors/scripts/run_salome_script.py /data/openfoam-10/run/of-bioreactors/scripts/make_stls.py -c "/data/openfoam-10/run/of-bioreactors/mesh_study/case_200000L/case_200000L_mesh2"
rm -r constant/polyMesh
blockMesh
mirrorMesh -dict /data/openfoam-10/run/of-bioreactors/configs/mirrorMeshDict.y -overwrite
mirrorMesh -dict /data/openfoam-10/run/of-bioreactors/configs/mirrorMeshDict.z -overwrite
transformPoints "Rz=90"
transformPoints "scale=(2710.6878788298623 10842.751515319449 2710.6878788298623)"
surfaceFeatures
snappyHexMesh -overwrite
snappyHexMesh -overwrite -dict system/snappyHexMeshDict.layers
renumberMesh -overwrite
topoSet -dict system/topoSetDict.liquid
