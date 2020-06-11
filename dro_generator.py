import os
from os.path import exists
import numpy as np
import imageio
import scipy.ndimage as ndi
import scipy.ndimage.morphology as morph
import scipy.ndimage.filters as filters
import pydicom
import datetime, time
import math
import imageio
import argparse
import yaml
import itertools
import png_to_dso
import shutil

# Collects User Input
parser = argparse.ArgumentParser(description="Upload Config and Output")
parser.add_argument('--config', '-c', action="store", required=False, help="Config File",default='config_dros.yaml')
parser.add_argument('--output', '-o', action="store", required=False, help="Output directory",default='Output/')

results = parser.parse_args()


# Set of Default Parameters
default_parameters = {
  # Size Features
  "mean_radius":        [100, 100, 1],
  # Shape Features
  "x_deformation":      [1, 1, 1],
  "y_deformation":      [1, 1, 1],
  "z_deformation":      [1, 1, 1],
  "surface_frequency":  [0, 0, 1],
  "surface_amplitude":  [0, 0, 1],
  # Intensity Features
  "mean_intensity":     [100, 100, 1],
  # Texture Features
  "texture_wavelength": [0, 0, 1],
  "texture_amplitude":  [0, 0, 1],
  # Margin Features
  "gaussian_standard_deviation":   [0, 0, 1]
}

# Keys in the Order for the DRO Name
ordered_keys = ["mean_radius", 
                "x_deformation","y_deformation", "z_deformation","surface_frequency", "surface_amplitude",
                "mean_intensity", 
                "texture_wavelength", "texture_amplitude", 
                "gaussian_standard_deviation"]

# process_input
# Takes:    raw yaml file received from the user 
# Does:     extracts all values into lists associated with each parameter
# Returns:  processed dictionary of parameters names as keys and lists of values 
def process_input(yml_file):
    with open(yml_file) as file:
        yaml_input = yaml.safe_load(file)
    try: 
        user_parameters = yaml_input["parameters"]
        if user_parameters is None:
            raise Exception("Empty Parameters Dictionary")
    except:
        print("Error in YAML File, Defaulting to Default Parameters")
        user_parameters = default_parameters
    for parameter in default_parameters:
        if parameter not in user_parameters or user_parameters[parameter] is None:
            user_parameters[parameter] =  default_parameters[parameter]
    return user_parameters

# expand_range
# Takes:    dictionary of parameters
# Does:     expands the min, max, number of values into array of values at equal intervals
# Returns:  dictionary of parameters with full arrays of values
def expand_range(dic):
    expanded = {}
    for key in dic.keys():
        kmax = dic[key][0]
        kmin = dic[key][1]
        knum = dic[key][2]
        expanded[key] = frange(kmin, kmax, knum)
    return expanded

# generate_params
# Takes:    dictionary of parameters with full arrays of values
# Does:     find all combinations of parameters of all ranges of values
# Returns:  array of all combinations of parameters
def generate_params(dic):
    params = []
    for key in ordered_keys:
        params.append(dic[key])
    params = list(itertools.product(*params))
    params = [list(p) for p in params]
    return params

# generate_all_dros
# Takes:    array of all combinations of parameters
# Does:     generates the images and masks for each combination of parameters
# Returns:  List of all folders for all images generated
def generate_all_dros(params, output):
    dicoms = []
    masks = []
    dsos = []
    for param in params:
        name, dicom, mask = generate_single_dro(param, output)
        dso = png_to_dso.make_dsos(mask, dicom, output)
        dicoms.append(dicom)
        masks.append(mask)
        dsos.append(dso)
    return [dicoms, masks, dsos]


# generate
# Takes:    list of arguments for a single DRO
# Does:     make unique ids for the dro
#           generate all files for the dro
# Return:   list of the name and locations of the dros files
def generate_single_dro(arguments, outpu):
    arguments = [float(arg) for arg in arguments]
    global r,  xx, yy, zz, shape_freq, shape_amp, avg, text_wav, text_amp, decay
    r,  xx, yy, zz, shape_freq, shape_amp, avg, text_wav, text_amp, decay = arguments
    make_folders(arguments, output)
    make_unique()
    mask, output_array = generate_dro()
    write_dro_files(mask, output_array)
    return [name, dicom_folder, mask_folder]


# make_folders
# Takes:    argument list for a single dro
# Does:     generate unique name for the dro
#           create dicom and mask folder for this dro
# Return:   nothing
def make_folders(arguments, output):
    global name
    name = 'Phantom'
    for arg in arguments:
        name = name + '-' + str(arg)

    global mask_folder, dicom_folder
    mask_folder = output+'Mask/'+name
    dicom_folder = output+'DICOM/'+name
    if not exists(mask_folder):
        os.makedirs(mask_folder)
    if not exists(dicom_folder):
        os.makedirs(dicom_folder)
    return []

# make_unique
# Takes:    nothing
# Does:     generate unique ids for the dro
# Return:   nothing
def make_unique():
    global instance_uid, instance_step
    instance_uid = pydicom.uid.generate_uid()[:-2] + ".1"
    instance_step = instance_uid

# Generate File by Slice
def write_dro_files(mask, output_array):
    n = np.shape(mask)[-1]
    print('dro generated')
    for k in range(n):
        # Once a complete 2D Slice has been generated, write this to png and dicom
        png_name = mask_folder+'/slice' + str(k).zfill(3) + '.png'
        mask_slice = mask[:, :, k].astype(np.uint8)
        imageio.imwrite(png_name, mask_slice)
        slice_to_write = output_array[:,:,k]
        write_dicom(slice_to_write, dicom_folder+'/slice' + str(k).zfill(3) + '.dcm', k,mask[:, :, k])


# generate_dro
# Takes:    nothing
# Does:     generate dro from its mathematical definition
# Return:   image array embedding the object and mask for the object
def generate_dro():
    n = 300
    s = 512
    # Make 3D Grid
    x = np.linspace(-s/2,s/2,s)
    y = np.linspace(-s/2,s/2,s)
    z = np.linspace(-n/2,n/2,n)
    xt, yt, zt = np.meshgrid(x,y,z,sparse=True) # xt stands for "x-true"
    if xx != 1 or yy != 1 or zz != 1:
        xs, ys, zs = np.meshgrid(1/float(xx)*x,1/float(yy)*y,1/float(zz)*z,sparse=True) # xs stands for "x stretch"
    else:
        xs, ys, zs = xt, yt, zt
    # Calculate distance to origin of each point then compare to the shape of the object 
    origin = np.sqrt(xs*xs + ys*ys + zs*zs)
    rp = r
    if shape_amp != 0.0 and shape_freq != 0.0:
        rp = r * (1 + shape_amp * np.sin(shape_freq * np.arccos(zs/origin)) * \
                                  np.cos(shape_freq * np.arctan2(ys,xs)))
    mask = rp >= origin
    # Apply Texture 
    texture = np.full_like(mask,1024,dtype=float)  
    if text_amp != 0.0 and text_wav != 0.0:
        variation = avg + text_amp * np.cos((1 / text_wav) * 2 * np.pi * xt) * \
                                     np.cos((1 / text_wav) * 2 * np.pi * yt) * \
                                     np.cos((1 / text_wav) * 2 * np.pi * zt)
        texture += variation
    else:
        texture += avg
    # Add blurred edge 
    if decay != 0:
        big = morph.binary_dilation(mask,iterations=10)
        texture[~big] = 0
        inside  = np.copy(texture)
        inside[~mask] = 0 
        texture = filters.gaussian_filter(texture,sigma=decay)
        output_array = texture
        texture[mask] = 0
        output_array = inside + texture 
    else:
        texture[~mask] = 0
        output_array = texture
    return mask, output_array


# prepare_zips
# Takes:    folders for dicoms, masks, and dsos
# Does:     zips all folders 
# Returns:  locations of all the zipped folders
def prepare_zips(dicoms, masks, dsos, output):
    top = os.path.dirname(os.path.dirname(os.path.dirname(dicoms[0])))
    cur = output #os.path.join(top,'output')
    for path in dicoms:
        if os.path.dirname(os.path.dirname(path)) != cur:
            move = os.path.join(cur,'DICOM',os.path.basename(path))
            os.rename(path,move)
    for path in masks:
        if os.path.dirname(os.path.dirname(path)) != cur:
            move = os.path.join(cur,'Mask',os.path.basename(path))
            os.rename(path,move)
    for path in dsos:
        if os.path.dirname(os.path.dirname(path)) != cur:
            move = os.path.join(cur,'DSO',os.path.basename(path))   
            os.rename(path,move)
    dizip = os.path.join(cur,'dicoms')
    mazip = os.path.join(cur,'masks')
    dszip = os.path.join(cur,'dsos')
    shutil.make_archive(dizip,  'zip', os.path.join(cur,'DICOM'))
    shutil.make_archive(mazip,  'zip', os.path.join(cur,'Mask'))
    shutil.make_archive(dszip,  'zip', os.path.join(cur,'DSO'))
    cleanup([os.path.join(cur,'DICOM'), os.path.join(cur,'Mask'), os.path.join(cur,'DSO')])
    return [dizip+'.zip', mazip+'.zip', dszip+'.zip']

# cleanup
# Takes:    top folder
# Does:     deletes everything 
# Returns:  nothing
def cleanup(big_folders):
    for folder in big_folders:
        shutil.rmtree(folder, ignore_errors=True)       



#Writes a DICOM file using an input array, filename, and slice number
def write_dicom(slice_to_write, filename, step,mask_slice):
    ds = pydicom.dcmread(curr + '/dro_template.dcm')

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
    ds.PatientSex = "O"

    (ds.Columns, ds.Rows) = slice_to_write.shape

    slice_to_write_unsign = slice_to_write.astype(np.uint16)

    ds.PixelData = slice_to_write_unsign.tostring()

    ds.SliceThickness = str(1)
    ds.ReconstructionDiameter = str(512.0)
    ds.PixelSpacing = [str(1),str(1)]

    ds.ImagePositionPatient[2] = str(float(ds.ImagePositionPatient[2]) - step * float(ds.SliceThickness))
    ds.SliceLocation = str(float(ds.SliceLocation) - step * float(ds.SliceThickness))

    ds.save_as(filename)
    return

# Create a numpy range 
def frange(start, stop, step):
    return np.linspace(start, stop, num=step).tolist()


if __name__ == '__main__':
    output = results.output
    curr          = os.path.dirname(os.path.abspath(__file__))
    processed_inputs = process_input(results.config)
    expanded_ranges  = expand_range(processed_inputs)
    full_param_list  = generate_params(expanded_ranges)
    dicoms, masks, dsos = generate_all_dros(full_param_list, output)
    #zips = prepare_zips(dicoms, masks, dsos, output)
    


