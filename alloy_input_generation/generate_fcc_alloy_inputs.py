import os
import pyemto
import numpy as np
from alloy_combinations import generate_combinations, elements

# It is recommended to always use absolute paths
folder = os.getcwd()                 # Get current working directory.
latpath = "/public/home/jcc/structures"   # Folder where the structure output files are.
emtopath = folder+"/fcc"  # Folder where the calculations will be performed.

# Generate combinations of elements
combo_size = 4
combinations_list = generate_combinations(elements, combo_size)

# Select the first combination
first_combination = combinations_list[0]

# Create the pyemto system
cocrfemnni = pyemto.System(folder=emtopath)

sws = np.linspace(2.50, 2.70, 11)  # 11 different volumes from 2.5 Bohr to 2.7 Bohr

# Set KGRN and KFCD values using a for loop.
# Use write_input_file functions to write input files to disk:
for i in range(len(sws)):
    cocrfemnni.bulk(lat='fcc',
                    jobname='1',
                    latpath=latpath,
                    atoms=[element for element in first_combination for _ in range(2)],
                    sws=sws[i],
                    amix=0.02,
                    efmix=0.9,
                    expan='M',
                    sofc='Y',
                    afm='M',         # Fixed-spin DLM calculation.
                    iex=7,           # We want to use self-consistent GGA (PBE).
                    nz2=16,
                    tole=1.0E-8,
                    ncpa=10,
                    nky=21,
                    tfermi=5000,
                    dx=0.015,        # Dirac equation parameters
                    dirac_np=1001,   # Dirac equation parameters
                    nes=50,          # Dirac equation parameters
                    dirac_niter=500) # Dirac equation parameters

    cocrfemnni.emto.kgrn.write_input_file(folder=emtopath)
    cocrfemnni.emto.kfcd.write_input_file(folder=emtopath)
    cocrfemnni.emto.batch.write_input_file(folder=emtopath)