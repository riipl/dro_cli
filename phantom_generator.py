import os
from os.path import exists
import numpy as np
from math import sqrt, atan2, acos, cos, sin, exp
import scipy.misc
import dicom
import datetime, time
import argparse

# Collects User Input
parser = argparse.ArgumentParser(description="Select Tumor Features")
parser.add_argument('--number','-n', action="store",required=False, help="Number of Z-Slices",default=100)
parser.add_argument('--radius','-r', action="store",required=False, help="Radius in mm",default=20)
parser.add_argument('--xdeformation','-x',action="store",required=False, help="X Deformation Scaling",default=1)
parser.add_argument('--ydeformation','-y',action="store",required=False, help="Y Deformation Scaling",default=1)
parser.add_argument('--zdeformation','-z',action="store",required=False, help="Z Deformation Scaling",default=1)
parser.add_argument('--decay', '-d', action="store", required=False, help="Exponential Decay Rate",default=0)
parser.add_argument('--frequency','-f', action="store", required=False, help="Bump Frequency",default=0)
parser.add_argument('--depth', '-b', action="store",required=False, help="Bump Depth",default=0)
parser.add_argument('--texture','-t', action="store", required=False, help="Texture Bump Diameter",default=0)
parser.add_argument('--dtexture','-u',action='store', required=False,help="3D textures",default=0)
parser.add_argument('--random','-q', action="store",required=False, help = "Random Noise Amplitude",default=0)
parser.add_argument('--size','-s', action="store_true",required=False, help = "Small Array", default=False)
parser.add_argument('--output', '-o', action="store", required=False, help="Output directory",default='Output/')
results = parser.parse_args()

# Sets Results to Variables
n = int(results.number)
r = float(results.radius)
xx = float(results.xdeformation)
yy = float(results.ydeformation)
zz = float(results.zdeformation)
decay = float(results.decay)
freq = float(results.frequency)
h = float(results.depth)
texture = float(results.texture)
new = bool(int(results.dtexture))
randy = float(results.random)
small = results.size
out = results.output

# Create Output Folders
name = 'Phantom-'+str(r)+'-'+str(xx)+'-'+str(yy)+'-'+str(zz)+'-'+str(decay)+'-'+str(freq)+'-'+str(h)+'-'+str(texture)+'-'+str(randy)+'-'+str(float(new))
print name
mask_folder = out+'Mask/'+name
dicom_folder = out+'DICOM/'+name
if not exists(mask_folder):
    os.mkdir(mask_folder)
if not exists(dicom_folder):
    os.mkdir(dicom_folder)

# Creates Instance Variable
instance_uid = dicom.UID.generate_uid()[:-1]+'.1'
instance_step = instance_uid

# Defines theta for the polar coordinates
def t(i,j):
    if i == 0:
        i = i + 50/float(s)
    return atan2(j,float(i))

#Defines phi for the polar coordinates
def p(i,j,k):
    if k == 0:
        k = k + 50/float(n)
    return acos(k/float(sqrt(i*i+j*j+k*k)))

#Writes a DICOM file using an input array, filename, and slice number
def write_dicom(input_array, filename, step):

    ds = dicom.read_file('phantom_framework.dcm')

    ds.ContentDate = str(datetime.date.today()).replace('-', '')

    global instance_step
    if step == 0:
        ds.file_meta.MediaStorageSOPInstanceUID = instance_uid
    else:
        instance_step = instance_step[:-5]+str(float(instance_step[-5:])+1)
        ds.file_meta.MediaStorageSOPInstanceUID = instance_step

    ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID
    ds.InstanceNumber = step + 1

    ds[0x0009,0x111e].value = ds.file_meta.MediaStorageSOPInstanceUID
    ds[0x0009,0x1146].value = ds.file_meta.MediaStorageSOPInstanceUID

    ds.StudyInstanceUID = instance_uid[:-1] + '5'
    ds.SeriesInstanceUID = instance_uid[:-1] + '6'

    ds.PatientName = name
    ds.PatientID = name

    (ds.Columns, ds.Rows) = input_array.shape

    input_array = input_array.astype(np.uint16)
    ds.PixelData = input_array.tostring()

    ds.SliceThickness = str(1)
    ds.ReconstructionDiameter = str(512.0)
    ds.PixelSpacing = [str(1),str(1)]

    ds.ImagePositionPatient[2] = str(float(ds.ImagePositionPatient[2]) - step * float(ds.SliceThickness))
    ds.SliceLocation = str(float(ds.SliceLocation) - step * float(ds.SliceThickness))

    ds.save_as(filename)
    return

# Initiates Two Numpy Arrays to Store Values
if small:
    s = 256
else:
    s = 512
mask = np.zeros((s,s,n))
output = np.zeros((s,s,n))

# Iterate through every i, j, k cell of the arrays
# Note: Will be faster in future to apply numpy functions to whole arrays
for k in range(n):
    z = zz * (-50 + k)           #
    uz = -50 + k
    for j in range(s):
        y = yy * (-256 + j)
        uy = -256 + j
        for i in range(s):
            x = xx * (-256 + i)
            ux = -256 + i

            if freq == 0.0:      # Set Shape with No surface bumps
                mask[i, j, k] = r >= sqrt(x*x+y*y+z*z)
            else:                # Set Shape with surface bumps
                mask[i,j,k] = (r + (h * r) * sin(freq * p(x, y, z)) * cos(freq * t(x, y))) >= sqrt(x*x+y*y+z*z)

            if mask[i,j,k]:
                value = 1500     # Set Average Value
                if decay != 0.0: # Apply Edge Decay Logarithmic Curve
                    e = exp(- decay * (sqrt(x * x + y * y + z * z) - r))
                    value *= e / (1 + e)
                if texture != 0.0:
                    if new:      # Apply 3D Texture Features
                        value += 500 * cos((1 / texture) * 2 * np.pi * ux) \
                                     * cos((1 / texture) * 2 * np.pi * uy) \
                                     * cos((1 / texture) * 2 * np.pi * uz)
                    else:        # Apply 2D Texture Features
                        value += 500 * cos((1 / texture) * 2 * np.pi * ux) \
                                     * cos((1 / texture) * 2 * np.pi * uy)
                if randy != 0.0: # Apply Random Noise
                    value += 500 * randy * np.random.random_sample()
                output[i,j,k] = value
            else:
                output[i,j,k] = 0

    png_name = mask_folder+'/slice' + str(k).zfill(3) + '.png'
    scipy.misc.imsave(png_name, mask[:, :, k])
    input_array = output[:,:,k]
    write_dicom(input_array, dicom_folder+'/slice' + str(k).zfill(3) + '.dcm', k)






