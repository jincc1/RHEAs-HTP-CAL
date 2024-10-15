import numpy as np
import pyemto
import os
import subprocess
import time
import sys
import csv

# local parameters
BMDL_DIR = '/public/home/jcc/structures/fcc/bmdl'
KSTR_DIR = '/public/home/jcc/structures/fcc/kstr'
SHAPE_DIR = '/public/home/jcc/structures/fcc/shape'

# sh parameters
partition = 'pms'
nodes = 1
ncpu = 32
runtime = '24:00:00'

# cal parameters
primitive = 'bcc'
species = [['Ti', 'V','Nb','Ta']]
concs = [[0.25, 0.25,0.25,0.25]]
# splts = [[1, -1]]  
sofc = 'Y'
find_primitive = False
make_supercell = None
coords_are_cartesian = True

# EOS parameters
xc = 'PBE'
method = 'morse'
units = 'bohr'

nkx = 41
nky = 41
nkz = 41

# Function to get job status
def get_job_status(job_ids):
    """Gets the status of jobs using squeue command."""
    cmd = ["squeue", "-j", ",".join(job_ids), "-o", "%i %t"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    output = result.stdout.strip()

    job_status = {}
    for line in output.split("\n")[1:]:
        current_job_id, current_job_status = line.split()
        job_status[current_job_id] = current_job_status
    return job_status

# Function to check job completion
def check_job_completion(job_ids):
    """Checks if all jobs are completed."""
    while True:
        time.sleep(5)
        job_status = get_job_status(job_ids)
        all_completed = True
        has_job_queuing = False
        for current_job_id, current_job_status in job_status.items():
            if current_job_status == "R":  # Running
                print(f"Job {current_job_id} is running...")
                all_completed = False
            elif current_job_status == "CF":  # Configuring
                print(f"Job {current_job_id} is configuring...")
                all_completed = False
            elif current_job_status == "PD":  # Pending
                print(f"Job {current_job_id} is pending...")
                all_completed = False
                has_job_queuing = True
            elif current_job_status == "CG":  # Completed
                print(f"{primitive} job {current_job_id} has completed")
            else:
                print(f"Job {current_job_id} status is {current_job_status}")
                all_completed = False

        if all_completed:
            print("All jobs completed!")
            break
        elif has_job_queuing:
            print("Jobs are queuing, waiting 2 minutes before checking again...")
            time.sleep(115)
        else:
            time.sleep(15)  # Check every 20 seconds if jobs are running
            print("Jobs are running, waiting 20 seconds before checking again...")

# Function to check if output files exist
def check_files(folder_name, file_name):
    """Checks if the specified file exists in the folder."""
    if not os.path.exists(f"{folder_name}") or not os.path.isdir(f"{folder_name}"):
        print(f"Error: Subfolder {folder_name} does not exist in the current directory.")
        sys.exit(1)

    shape_path = os.path.join(f"{folder_name}", f"{file_name}")
    if os.path.exists(shape_path):
        print(f"{folder_name}/{file_name} exists. Job completed successfully.")
    else:
        print(f"Job exited abnormally: Output file {file_name} not found.")
        sys.exit(1)

# Function to define input parameters
def inp_parameter(BMDL_DIR,KSTR_DIR,SHAPE_DIR,lat, jobname, species, sws, amix, efmix, sofc, iex, nz2, ncpa, nky, xc, method, EMTOdir):
    folder = os.getcwd()  # Get current directory
    latpath = folder  # CPA structure output file location
    emtopath = folder  # EMTO calculation output file location
    heas = pyemto.System(folder=emtopath, EMTOdir=EMTOdir)
    heas.bulk(lat=lat,
              jobname=jobname,
              latpath=latpath,
              atoms=species,
              sws=sws)  # Dirac equation parameters

    return heas


# Function to extract parameters from output files
def extract_parameters(file_path, keyword):
    try:
        with open(file_path) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if keyword in line:
                    param_line = lines[i].strip()
                    parameters = param_line.split()
                    return parameters
            print(f"Parameter {keyword} not found. Please check the file.")
            return None
    except:
        print(f"Error finding parameter {keyword}. Please check the file.")
        return None


# Function to check if a number is within a range
def is_within_range(num, min_num, max_num):
    if num >= min_num and num <= max_num:
        return True
    else:
        return False


# Function to write data to a CSV file
def write_to_csv(data, filename, headers):
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        # Only write headers if the file is empty
        if f.tell() == 0:
            writer.writerow(headers)
        writer.writerow(data)


# Primitive bcc
if primitive == 'bcc':
    prims0 = np.array([
        [0.5, 0.5, -0.5],
        [0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.5]])
# Primitive fcc
if primitive == 'fcc':
    prims0 = np.array([
        [0.5, 0.5, 0],
        [0.5, 0, 0.5],
        [0, 0.5, 0.5]])


basis0 = np.array([
    [0.0, 0.0, 0.0]
])

folder = os.getcwd()
emtopath = folder
latpath = emtopath


slurm_options = [f'#SBATCH -n {ncpu}',
                 f'#SBATCH --nodes={nodes}',
                 f'#SBATCH --partition={partition}'
                 ]


deltas = np.linspace(0, 0.05, 6)
# We need to use a non-zero value for the first delta to break the symmetry of the structure.
deltas[0] = 0.001

# Only two distortions for cubic (third one is bulk modulus EOS fit)
distortions = ['Cprime', 'C44']

jobname = ''
for i in range(len(species)):
    for j in range(len(species[i])):
        jobname += "{}".format(species[i][j])
print("Generating lattice constant input files...")
while True:
    # Redirect output to buffer
    sys.stdout = StringIO()

    # Calculate equilibrium volume
    for i, distortion in enumerate(distortions):

        if i > 0:
            pass

        input_creator = EMTO(folder=emtopath, EMTOdir=emtodir)
        input_creator.prepare_input_files(latpath=latpath,
                                          jobname=jobname,
                                          species=species,
                                          # afm =afm,
                                          # splts=splts,
                                          concs=concs,
                                          prims=prims0,
                                          basis=basis0,
                                          find_primitive=find_primitive,
                                          coords_are_cartesian=coords_are_cartesian,
                                          latname=primitive,
                                          nz1=32,
                                          ncpa=10,
                                          sofc=sofc,
                                          nkx=nkx,
                                          nky=nky,
                                          nkz=nkz,
                                          ncpu=ncpu,
                                          parallel=False,
                                          alpcpa=0.9,
                                          runtime=runtime,
                                          KGRN_file_type='scf',
                                          KFCD_file_type='fcd',
                                          amix=0.01,
                                          # efgs=-1.0,
                                          depth=0.75,
                                          tole=1e-5,
                                          tolef=1e-5,
                                          iex=4,
                                          niter=100,
                                          kgrn_nfi=31,
                                          # strt='B',
                                          make_supercell=make_supercell,
                                          slurm_options=slurm_options)
        input_creator.write_kgrn_kfcd_swsrange(sws=sws_range)
# Close buffer
sys.stdout = open(1, 'w', closefd=False)
print("Lattice constant files generated!")

# Submit lattice job and save job ID
print(primitive, "structure job submitting...")
cmd = f'sbatch {primitive}.sh'
result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
output = result.stdout.decode()

# Get job ID
job_id = [output.strip().split()[-1]]
print(primitive, " structure job submitted, ID is:", job_id[0])

# Call functions to check job completion and file existence
print("Checking structure job status...")
check_job_completion(job_id)
print("Checking structure job output files...")
check_files("shape", f"{primitive}.shp")

# Write EOS script file into a sh file
print("Submitting lattice constant jobs...")
with open('sbatch_eos.sh', 'w') as f:
    for i in range(len(sws_range)):
        f.writelines(f'sbatch  {jobname}_{sws_range[i]:.6f}.sh\n')

# Submit EOS script file and get job status
cmd = ["bash", "sbatch_eos.sh"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

# Read command output line by line and get job IDs
job_ids = []
for line in proc.stdout:
    out = line.decode().strip()
    if out.startswith("Submitted batch job"):
        job_id = out.split()[-1]
        job_ids.append(job_id)

# Call functions to check job completion and file existence
print("Checking lattice constant job status...")
check_job_completion(job_ids)
print("Checking lattice constant output files...")
for i in range(len(sws_range)):
    check_files("kfcd", f"{jobname}_{sws_range[i]:.6f}.prn")

# Call function to get input parameters
print("Analyzing lattice constants...")
heas = inp_parameter(primitive, jobname, species[0], sws_range[0], '0.01',
                     '0.9', sofc, '4', '16', '15', nky, xc, method, emtodir)

# Redirect output to buffer
sys.stdout = StringIO()

# Call function to analyze lattice constants
result = heas.lattice_constants_analyze(sws=sws_range)

# Get content from buffer
output = sys.stdout.getvalue()

# Write content to file
with open('lattice_constants.txt', 'w') as f:
    f.write(output)

# Close buffer
sys.stdout = open(1, 'w', closefd=False)
print("Lattice constants saved in lattice_constants.txt...")
print("Checking if sw is within the specified range")
# Get the variance of the EOS curve fitting, exit the program if it is too low
r_squared = extract_parameters('lattice_constants.txt', 'R squared')
r_squared = float(r_squared[3])
print(f"Variance of EOS fitting curve is {r_squared:.8f} ")
if r_squared < 0.9:
    print("EOS curve fitting is too poor, it is recommended to reselect the WS radius for calculation")
    sys.exit()
# Get the WS radius with the lowest energy
sws0 = extract_parameters('lattice_constants.txt', 'sws0')
# print(f"The WS cell radius with the lowest energy is {float(sws0[2]):.6f} {sws0[3]}")
sws0 = float(sws0[2])

# Determine if it is within the range

if is_within_range(sws0, sws_range[0], sws_range[-1]):
    print(f"The WS radius with the lowest energy is {float(sws0):.6f}, within the specified range")
    break
else:
    print(f"The WS radius with the lowest energy is {float(sws0):.6f}, not within the specified range")
    values = sws0 + np.arange(-2,3) * 0.01
    num_values = 5
        sws_range = values[:num_values]

print(f"sw radius is {float(sws0):.6f} ")

E0 = extract_parameters('lattice_constants.txt', 'E0')
print(f"Lowest energy is {float(E0[2]):.6f} ")
E0 = float(E0[2])

# Get bulk modulus
B0 = extract_parameters('lattice_constants.txt', 'B0')
B0 = float(B0[2])
print(f"Bulk modulus is {B0:.6f} ")

# Get volume and calculate elastic constants
V0 = extract_parameters('lattice_constants.txt', 'V0')
V0 = float(V0[2])
if primitive == 'bcc':
    lattice_constants = (V0 * 2) ** (1 / 3)
    print(f"{jobname} {primitive} lattice constant is {lattice_constants:.6f} ")
elif primitive == 'fcc':
    lattice_constants = (V0 * 4) ** (1 / 3)
    print(f"{jobname} {primitive} lattice constant is {lattice_constants:.6f} ")
else:
    print(f"Please check the input lattice type: {primitive} ")

print("Lattice constant job analysis completed, preparing input files for elastic constants...")

# Create ela folder
ela_folder_name = 'ela'
if not os.path.exists(ela_folder_name):
    os.makedirs(ela_folder_name)
    print(f"{ela_folder_name} folder created!")
else:
    print(f"{ela_folder_name} folder already exists!")

# Enter ela folder
os.chdir('ela')

# Get the lowest WS radius
print("Generating elastic constant input files...")
sws_range = np.array([sws0])
folder = os.getcwd()  # Get current directory
latpath = folder  # CPA structure output file location
emtopath = folder  # EMTO calculation output file location

# Redirect output to buffer
sys.stdout = StringIO()
for i, distortion in enumerate(distortions):
    for delta in deltas:
        # These distortion matrices are from the EMTO book.

        if distortion == 'Cprime':
            dist_matrix = np.array([
                [1 + delta, 0, 0],
                [0, 1 - delta, 0],
                [0, 0, 1 / (1 - delta ** 2)]
            ])

        elif distortion == 'C44':
            dist_matrix = np.array([
                [1, delta, 0],
                [delta, 1, 0],
                [0, 0, 1 / (1 - delta ** 2)]
            ])

        # Calculate new lattice vectors and atomic positions
        prims = distort(dist_matrix, prims0)
        basis = distort(dist_matrix, basis0)

        # Each different distortion might need different set of nkx, nky, nkz
        if distortion == 'Cprime':
            nkx = 41;
            nky = 41;
            nkz = 41
        elif distortion == 'C44':
            nkx = 40;
            nky = 40;
            nkz = 45

        input_creator = EMTO(folder=emtopath, EMTOdir=emtodir)
        input_creator.prepare_input_files(latpath=latpath,
                                          jobname=f'{jobname}_d{i + 1}_{delta:4.2f}',
                                          species=species,
                                          # afm=afm,
                                          # splts=splts,
                                          concs=concs,
                                          prims=prims,
                                          basis=basis,
                                          find_primitive=find_primitive,
                                          coords_are_cartesian=coords_are_cartesian,
                                          latname='d{0}_{1:4.2f}'.format(i + 1, delta),
                                          # nz1=32,
                                          ncpa=15,
                                          sofc=sofc,
                                          nkx=nkx,
                                          nky=nky,
                                          nkz=nkz,
                                          ncpu=ncpu,
                                          parallel=False,
                                          alpcpa=0.8,
                                          runtime=runtime,
                                          KGRN_file_type='scf',
                                          KFCD_file_type='fcd',
                                          amix=0.01,
                                          #efgs=-1.0,
                                          depth=0.7,
                                          tole=1e-5,
                                          tolef=1e-5,
                                          iex=4,
                                          niter=200,
                                          kgrn_nfi=91,
                                          #strt='B',
                                          make_supercell=make_supercell,
                                          slurm_options=slurm_options)
        

        input_creator.write_kgrn_kfcd_swsrange(sws=sws_range)
        
        output = sys.stdout.getvalue()
    
sys.stdout = open(1, 'w', closefd=False)

with open('sbatch_lat.sh', 'w') as f:
    f.writelines('#!/bin/bash\n')
    for i, distortion in enumerate(distortions):
        for delta in deltas:                    
            f.writelines(f'sbatch  d{i+1}_{delta:4.2f}.sh\n')

with open('sbatch_ela.sh', 'w') as f:
    f.writelines('#!/bin/bash\n')
    for i, distortion in enumerate(distortions):
        for delta in deltas:
            f.writelines(f'sbatch  {jobname}_d{i+1}_{delta:4.2f}_{sws_range[0]:.6f}.sh\n')

cmd = ["bash", "sbatch_lat.sh"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

job_ids = []
for line in proc.stdout:
    out = line.decode().strip()
    if out.startswith("Submitted batch job"):
        job_id = out.split()[-1]
        job_ids.append(job_id)
        

check_job_completion(job_ids)  

for i, distortion in enumerate(distortions):
    for delta in deltas:                    
        check_files("shape",f'd{i+1}_{delta:4.2f}.shp')


cmd = ["bash", "sbatch_ela.sh"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        

job_ids = []
for line in proc.stdout:
    out = line.decode().strip()
    if out.startswith("Submitted batch job"):
        job_id = out.split()[-1]
        job_ids.append(job_id)



check_job_completion(job_ids) 


for i, distortion in enumerate(distortions):
    for delta in deltas:
        check_files("kfcd",f'{jobname}_d{i+1}_{delta:4.2f}_{sws_range[0]:.6f}.prn')
        
j=0
k=0
try:
    kfcdpath ='./kfcd'
    os.chdir(kfcdpath)
    for i, distortion in enumerate(distortions):
        for delta in deltas:
            oldname = f'{jobname}_d{i+1}_{delta:4.2f}_{sws_range[0]:.6f}.prn'
            if i==0:
                newname = f'{jobname}_{primitive}o{j}_{sws_range[0]:.6f}.prn'
                if os.path.exists(newname):                
                    break
                j+=1
            if i==1:
                newname = f'{jobname}_{primitive}m{k}_{sws_range[0]:.6f}.prn'
                if os.path.exists(newname):
                    break
                k+=1
            os.rename(oldname,newname)
finally: 
    os.chdir('..')
    heas = inp_parameter(primitive,jobname,species[0],sws_range[0],'0.01',
        '0.9', sofc,'4','16', '15', nky,xc,method,emtodir)
        
    sys.stdout = StringIO()
    result = heas.elastic_constants_analyze(sws=sws_range[0],bmod=B0)

    output = sys.stdout.getvalue()


    with open('elastic_constants.txt', 'w') as f:
        f.write(output)
    sys.stdout = open(1, 'w', closefd=False)
    
    print("elastic_constants.txt")


    c11 = extract_parameters('elastic_constants.txt', 'c11(GPa)')
    c11 = float(c11[2])
    print(f'C11 = {c11} GPa')
    
    c12 = extract_parameters('elastic_constants.txt', 'c12(GPa)')
    c12 = float(c12[2])
    print(f'C12 = {c12} GPa')
    
    c44 = extract_parameters('elastic_constants.txt', 'c44(GPa)')
    c44 = float(c44[2])
    print(f'C44 = {c44} GPa')    
    
    BH = extract_parameters('elastic_constants.txt', 'BH(GPa)')
    BH = float(BH[2])
    print(f'BH = {BH} GPa')  
    
    GH = extract_parameters('elastic_constants.txt', 'GH(GPa)')
    GH = float(GH[2])
    print(f'GH = {GH} GPa')

    EH = extract_parameters('elastic_constants.txt', 'EH(GPa)')
    EH = float(EH[2])
    print(f'EH = {EH} GPa')    
    
    vH = extract_parameters('elastic_constants.txt', 'vH(GPa)')
    vH = float(vH[2])
    print(f'vH = {vH} GPa')

    AVR = extract_parameters('elastic_constants.txt', 'AVR(GPa)')
    AVR = float(AVR[2])
    print(f'AVR = {AVR} GPa')


    os.chdir(datadir)
    headers = ['System']
    headers.extend(['Element {}'.format(i) for i in species[0]])
    headers.extend(['r_squared','sws0','lattice_constants','E0','C11','C12','C44','B','G','E','v','AVR'])

    data = [f'{jobname}']
    data.extend([f'{i}' for i in concs[0]])
    data.extend([f'{r_squared:.6f}',f'{sws0:.6f}',f'{lattice_constants:.6f}',f'{E0}',f'{c11}',f'{c12}',
        f'{c44}',f'{BH}',f'{GH}',f'{EH}',f'{vH}',f'{AVR}'])
    write_to_csv(data, 'data.csv',headers)