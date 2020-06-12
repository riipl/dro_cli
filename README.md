# dro_cli
Command Line Tool for Stanford Digital Reference Object Generation

The command line tool generates any number of user-specified digital reference objects for radiomic feature harmonization. The tool has been developed and provided by the Radiological Image and Information Processing Lab.

dro_generator.py hosts the main interface for generating the dros   
config_dros.yaml is a sample yml configuration file for the dro generator   
png_to_dso.py offers a script for converting the resulting DICOM and Mask folders to a DSO   
epad-ws-1.1-jar-with-dependencies.jar is a java package that generates DSOs. This is used within png_to_dso.py   
dro_template.dcm is a dicom that contains a template that the synthetic dicom headers are built off of.   

A simple example use case of this code is:
python dro_generator.py -c config_dros.yaml -o  Output/

A 32-object sample collection of these DROs has been generated, hosted, and described in the following TCIA source and Tomography paper:
TCIA Data Citation: 
Jaggi, A., Mattonen, S., McNitt-Gray, M., & Napel, S. (2020).  Data from the Stanford DRO Toolkit: Digital Reference Objects for Standardization of Radiomic Features  [Data set]. The Cancer Imaging Archive.  https://doi.org/10.7937/t062-8262
Tomography Paper Citation:
Jaggi, A., Mattonen, S., McNitt-Gray, M., Napel, S (2020). Stanford DRO Toolkit: Digital Reference Objects for Standardization of Radiomic Features. (In Press) Tomography, Jun. 2020. https://doin.org/10.18383/j.tom.2019.00030 

A 3-object subset of that sample collection was used and shared in the following TCIA source and Tomography paper:
TCIA Data Citation:
McNitt-Gray, M.*, Napel, S.*, et. al. (2020). Data from the  Standardization in Quantitative Imaging: A Multi-center Comparison of Radiomic Feature Values [Data set]. The Cancer Imaging Archive. DOI: https://doi.org/10.7937/tcia.2020.9era-gg29.
Tomography Paper Citation:
McNitt-Gray, M.*, Nape, S.*, et. al. (2020). Standardization in Quantitative Imaging: A Multi-center Comparison of Radiomic Feature Values, Tomography. https://doi.org/10.18383/j.tom.2019.00031.


For questions:
Akshay Jaggi
Email: ajaggi@stanford.edu
