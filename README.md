_______________________________________________________________________________

	___  __  __ ___   __  __ _       ___                    
	|   \|  \/  |_ _| |  \/  | |     / __|_ _ ___ _  _ _ __   Lucas Brito, Rob 
	| |) | |\/| || |  | |\/| | |__  | (_ | '_/ _ \ || | '_ \  Scheidegger, Nadav
	|___/|_|  |_|___| |_|  |_|____|  \___|_| \___/\_,_| .__/  Druker, Zach Rosen- 
							  |_|     feld, Summer 2021.
______________________________________________________________________________


# Folder Organization

To keep things from getting out of hand, here is a brief description of how the folder structure should work:

1. `src` directly contains all executable python files, and any files with shared/extensible functions should be placed in `src/api`.
2. `files` contains all small data files that are required for folder/project management, and is part of the git repo.
3. `outputs` should be all of the outputs of the slurm scripts (`.out` files), and is gitignored.
4. `data` is for large data files such as training data and models, and is also gitignored.


# Running Scripts

To run a script: 

	sbatch [OPTIONS] run_script.sh SCRIPT

For example:

	sbatch -n 8 -t 00:10:00 --mem=16G --output=output.out run_script.sh script.py

will use 16GB of memory and eight cores and output the file under output.out in 10 minutes or less (or else terminate the job). 

Most scripts have default run .sh files which have the proper settings (e.g., 
walltime, number of cores). To run these

	./scripts/RUN_SCRIPT

Common options:

	-n          : number of tasks (= number of cores if -c not specified)
	-c          : number of cores per task
	-t          : runtime in HH:MM:SS
	--mem       : memory per node 
	-o          : output filename 
	--mail-type : events for which email notifications will be sent: BEGIN,
		      END, FAIL, REQUEUE, ALL
	--mail-user : mail ID where you will be notified  

IMPORTANT: SLURM outputs are not accessible to other users by default. Use 

	chmod ugo+rwx FILENAME
to make sure other group members can read and write this file. In the case of 
a directory, run 

	chmod -R ugo+rwx DIRNAME 

_______________________________________________________________________________

# Virtual Environment

On Oscar, the python environment with all of the project dependencies is located in 
~/data/dmi/dmi/ (it is virtual env in the dmi directory). To activate this 
environment:

	source ~/data/dmi/dmi/bin/activate
_______________________________________________________________________________
# Installing Packages

To install packages: make sure you load the proper Python module before you 
use pip install. First load 3.7.4:

	module load python/3.7.4

Then activate the environment

	source ~/data/dmi/dmi/bin/activate

Then use pip as you would normally:

	pip install PACKAGE	
_______________________________________________________________________________

# Misc Utilities

To remove any outputs under the default `slurm-******.out` filename, run 

	./scripts/delete_slurm_outs.sh
_______________________________________________________________________________

This readme written by Lucas and since edited by Rob, last updated September 13th, 2021.
