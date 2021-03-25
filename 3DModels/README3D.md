# Three dimensional models
This folder contains MITgcm configuration files used for the three dimensional model integrations.

## Models present
The four different configurations present are:
- Standard no-slip
- Standard free-slip
- Viscous no-slip
- Viscous free-slip

## Requirements
The model was run using 192 processors (8 nodes) on ARCHER, the UK's national HPC facility. The code supplied here, when built, should run on this system. You will also need a copy of the MITgcm, available at https://github.com/MITgcm/MITgcm. The published results were run with the checkpoint67r version: https://github.com/MITgcm/MITgcm/releases/tag/checkpoint67r.

## Building the model
You should build the model by running genmake2 in the build directory as outlined in the MITgcm docs: https://mitgcm.readthedocs.io/en/latest/getting_started/getting_started.html#generating-a-makefile-using-genmake2. You should specify an appropriate option file  and enable mpi when you do this. You can then run the `make` command to produce the `mitgcmuv` exacutable. The commands you run within the build directory will look something like
```
export $MITGCM=<<PATH TO MITGCM>>

$MITGCM/tools/genmake2 -mods=../code -of=$MITGCM/tools/build_options/<<YOUR SYSTEM'S OPTFILE>> -rd=$MITGCM -mpi

make depend
make
```

## Running the model
Create a directory in which to run the model. Copy over the contents of one of the configuration folders. You will need to unzip the folder of input files. You should link the executable from the build directory to the run folder also. Within the run directory the commands you run will look something like
```
cp ../StandardNoSlip/* ./
tar -xzvf ./input.tar.gz ./input
ln -s ../build/mitgcmuv ./
```
You are then ready to run your job using the appropriate `mpiexec` type command, or your system's queueing facility. 
