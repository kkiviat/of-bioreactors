python3 /data/openfoam-10/run/of-bioreactors/scripts/run_salome_script.py /data/openfoam-10/run/of-bioreactors/scripts/make_stls.py -c .
rm -r constant/polyMesh
blockMesh
mirrorMesh -dict /data/openfoam-10/run/of-bioreactors/configs/mirrorMeshDict.y -overwrite
mirrorMesh -dict /data/openfoam-10/run/of-bioreactors/configs/mirrorMeshDict.z -overwrite
transformPoints "Rz=90"
transformPoints "scale=(1258.1898589786201 5032.7594359144805 1258.1898589786201)"
surfaceFeatures
snappyHexMesh -overwrite
snappyHexMesh -overwrite -dict system/snappyHexMeshDict.layers
renumberMesh -overwrite
topoSet -dict system/topoSetDict.liquid
