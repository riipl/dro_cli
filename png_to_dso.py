import scipy.misc
import os
from os import listdir, mkdir, getcwd
from os.path import isfile, isdir, join, exists
import shutil
import argparse
import time


parser = argparse.ArgumentParser(description="Convert PNG to DSO")
parser.add_argument('--png', '-p', action="store", required=True, help="PNG Folder Path")
parser.add_argument('--dicom', '-d', action="store", required=True, help="Dicom Folder Path")
parser.add_argument('--output', '-o',action="store",required=True,help="Output Folder Path")
results = parser.parse_args()

#Path to GIPL
pngs = results.png

#Path to DICOMS
dicoms = results.dicom

#Path to Output
output = results.output

#Path to EPAD
file_jar = "epad-ws-1.1-jar-with-dependencies.jar"

#Iterate through pngs in pngs folder

tmp_dir = output+"temp"
if exists(tmp_dir):
    shutil.rmtree(tmp_dir)
mkdir(tmp_dir)

i = 0
for filename in sorted(os.listdir(pngs)):
    if filename.endswith(".png"):
        img = scipy.misc.imread(pngs+filename)
        img_name = str(i).zfill(3) + '.tif'
        scipy.misc.imsave(join(tmp_dir, img_name), img)
        i+=1

dso_name = output + dicoms[dicoms.rfind('/',0,len(dicoms)-1):-1]+'.dcm'
tif_path = tmp_dir.replace(' ', '\\ ').replace('(', '\\(').replace(')','\\)')
dso_name = dso_name.replace(' ', '\\ ').replace('(', '\\(').replace(')','\\)')

commandS = 'java -classpath epad-ws-1.1-jar-with-dependencies.jar edu.stanford.epad.common.pixelmed.TIFFMasksToDSOConverter ' + tmp_dir + ' ' + dicoms + ' ' + dso_name
print commandS + "\n"
print os.system(commandS)
shutil.rmtree(tmp_dir)

