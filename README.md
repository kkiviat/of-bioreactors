# Prerequisites
These cases are configured for use with OpenFOAM 10. The case setup scripts rely on PyFoam and Salome (used Salome 9.10.0). A docker image [kkiviat/openfoam](https://hub.docker.com/r/kkiviat/openfoam) with the necessary software can be obtained from dockerhub.

If you are not using the docker image this way, you can configure the root directory in `default.parameters` in each case to point to the root directory of this repository. You may also need to change the path to Salome in `scripts/run_salome_script.py`.

# Setup
Clone this repo into the OpenFOAM `run` directory. The scripts expect the path to be under `OpenFOAM/openfoam-10/run/of-bioreactors`. If you change this, you will need to update the `project_root`  in the case's `default.parameters`.

Compile the `strainRate` function object, located under `functionObjects/strainRate`. To do so, you need to be in the docker image or have OpenFOAM installed.

```sh
cd functionObjects/strainRate
wmake
```

To use the docker image, run a command like this. This mounts the OpenFOAM directory under `/data` in the container, sets the user id to the current id to ensure access to the files, and sets the working directory to `/data`. Here `<path_to_OpenFOAM_dir>` refers to the OpenFOAM directory that is the parent of `openfoam-10/run/of-bioreactors`.

```sh
docker container run -ti --shm-size=1024M --rm -u $(id -u):$(id -g) -v <path_to_OpenFOAM_dir>:/data:z -w /data kkiviat/openfoam:10 bash
```

Note: The cases in this repo were run with the image `kkiviat/openfoam:10`. Version `10.1` is the same except that it has ParaView 5.12.1 installed instead of the default 5.10.

# Configuring cases
Each case has a `derivedParameters.py` file which constructs a geometry configuration. Currently they all call a method in `scripts/geometry_builder.py` to construct a geometry based only on the case volume. Those functions can be modified or new ones added to define different geometries.

The operating conditions are specified in the `default.parameters` file in each case directory, including superficial gas velocity (v_s), agitation rate (RPM), bubble size, drag model, and more.

# Running cases
To set up dictionaries from the templates:
```sh
sh init_params.sh
```

To set up the mesh:
```sh
sh set_up_mesh.sh
```

To set up the case to run on `n` processors:
```sh
sh set_up_case.sh <n>
```

To run the case and save output in `log.solver`:
```sh
mpirun -n <n> multiphaseEulerFoam -parallel &>> log.solver &
```

# Building Docker image

The dockerfiles under `docker/` are based on https://github.com/jakobhaervig/openfoam-dockerfiles

You can download the image from dockerhub via
```sh
docker pull kkiviat/openfoam:10
```

But if you want to build it locally, use
```sh
docker image build --no-cache -t openfoam:10 docker/openfoam
docker image build -t openfoam:10 docker/python
```

To include ParaView 5.12.1, also run
```sh
docker image build -t openfoam:10 docker/paraview512
```
