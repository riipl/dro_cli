import csv
import numpy as np
import argparse
import pandas

parser = argparse.ArgumentParser(description="Select CSV File for Analysis")
parser.add_argument('--input', '-i', action="store", required=True, help="Input CSV File")
results = parser.parse_args()
input = results.input

#import data
df = pandas.read_csv(input,header=[0,1])
df = df[0:11]

# Normalize
mins = df.min(axis=1,level=1)
maxs = df.max(axis=1,level=1)
bottoms = maxs - mins
tops = df.subtract(mins,level=1)
norm = tops.divide(bottoms,level=1)

# Write to CSV
norm.to_csv(input+'_textures.csv')

