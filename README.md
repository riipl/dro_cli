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


For questions:
Akshay Jaggi
Email: ajaggi@stanford.edu
