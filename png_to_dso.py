import imageio
import os
from os import listdir, makedirs, getcwd
from os.path import isfile, isdir, join, exists
import subprocess
import shutil
import time
import shlex

#Path to EPAD
curr = os.path.dirname(os.path.abspath(__file__))
file_jar = curr + "/epad-ws-1.1-jar-with-dependencies.jar"
pngs = ''
dicoms = ''
tmp_dir = ''

# Make DSOs
# Input: png location, dicom location
# Does:  sets these to global variables
#		 creates temporary folder of tiffs
#		 Reads tiff from location and generates dso using java
#        Returns location of dso 
def make_dsos(in_pngs, in_dicoms, output_top):
	output = os.path.join(output_top,"DSO")
	global pngs, dicoms
	pngs = in_pngs
	dicoms = in_dicoms
	make_temp(output)
	make_tiffs()
	return make_dso(output)

# make_temp
# Does: Generates temporary directory
def make_temp(output):
	global tmp_dir
	tmp_dir = output+'/temp'
	if exists(tmp_dir):
	    shutil.rmtree(tmp_dir)
	makedirs(tmp_dir)

# make_tiffs
# Does: Fills temporary directory with tiffs instead of pngs
def make_tiffs():
	i = 0
	for filename in sorted(os.listdir(pngs)):
	    if filename.endswith(".png"):
	        img = imageio.imread(pngs+'/'+filename)
	        img_name = str(i).zfill(3) + '.tif'
	        imageio.imsave(join(tmp_dir, img_name), img)
	        i+=1

# make_dso
# Does: Corrects any operating system issues with file naming
#       Runs epad jar to generate dsos
def make_dso(output):
	dso_name = output + dicoms[dicoms.rfind('/',0,len(dicoms)-1):]+'.dcm'
	tif_path = tmp_dir
	tmp_dir_fixed = tmp_dir.replace('\\','/')
	dicoms_fixed = dicoms.replace('\\','/')
	dso_name_fixed = dso_name.replace('\\','/')
	file_jar_fixed = file_jar.replace('\\','/')
	commandS = 'java -classpath ' + file_jar_fixed + ' edu.stanford.epad.common.pixelmed.TIFFMasksToDSOConverter ' + tmp_dir_fixed + ' ' + dicoms_fixed + ' ' + dso_name_fixed
	#commandS = ['java', '-classpath', file_jar, 'edu.stanford.epad.common.pixelmed.TIFFMasksToDSOConverter ', tmp_dir_fixed, dicoms_fixed, dso_name_fixed]
	subprocess.call(commandS,shell=True)
	shutil.rmtree(tmp_dir)
	return dso_name

