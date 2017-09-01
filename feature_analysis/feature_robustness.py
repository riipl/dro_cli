import numpy as np
import argparse
import matplotlib.pyplot as plt
import csv

# Collect Input File
parser = argparse.ArgumentParser(description="Select CSV File for Analysis")
parser.add_argument('--input', '-i', action="store", required=True, help="Input CSV File")
parser.add_argument('--feature','-f', action='store', required=True, help="Feature to Analyze")
results = parser.parse_args()
input = results.input
f = results.feature

# Load CSV FIle
data = np.genfromtxt(input,delimiter=',',names=True,dtype=None)

#Sort
if f == 't':
    parameters = ['r','x', 'd', 'f', 't']
    title = 'Texture Frequency'
elif f == 'f':
    parameters = ['r', 'x', 'd', 't','f']
    title = 'Shape Frequency'
elif f == 'd':
    parameters = ['r', 'x', 'f', 't', 'd']
    title = 'Edge Sharpness'
elif f == 'x':
    parameters = ['r', 'd', 'f', 't', 'x']
    title = 'X-Deformation'
else:
    parameters = ['x','d', 'f', 't', 'r']
    title = 'Radius'

data = np.sort(data, order = parameters)

#Find Features
names = data.dtype.names
featurenames = []
for name in names:
    if str(data[name].dtype) != '|S58' and str(data[name].dtype) != '|S47' and name not in parameters:
        featurenames.append(name)

featurelist = {'size':0,'intensity':1,'sphericity':2,'roughness':3,'edge':4,'lvii':5,'glcm':6}
features = []
iter = 0
for name in names:
    for feature in featurelist.keys():
        if name.find(feature) >=0:
            features.append(featurelist[feature])
            break
    iter+=1


#Find Min and Max
cols = np.shape(data)[0]
rows = np.shape(names)[0]

mins = np.zeros((rows,1))
maxs = np.zeros((rows,1))

iter = 0
for name in names:
    if str(data[name].dtype) != '|S58' and str(data[name].dtype) != '|S47':
        mins[iter] = np.nanmin(data[name])
        maxs[iter] = np.nanmax(data[name])
    iter+=1

#Normalize
remove =  len(names) - len(featurenames)
removed = len(featurenames)
norms = np.zeros((cols,removed))
iter = 0
for name in names:
    if str(data[name].dtype) != '|S58' and str(data[name].dtype) != '|S47' and name not in parameters:
        w = maxs[iter] - mins[iter]
        norms[:,iter-remove] = [(i-mins[iter])/w if w !=0 else i for i in data[name]]
    iter+=1

#Find Deltas
deltas = np.zeros((cols/2,removed))
for i in range(cols/2):
    deltas[i,:] = norms[2*i+1,:]-norms[2*i,:]

#Collect Mean and Std Dev
avgs = np.mean(deltas,axis=0)
absavgs = np.mean(np.absolute(deltas),axis=0)
devs = np.std(deltas,axis=0)

#Write Values to CSV
with open('DataSet1/r-'+title + '-output.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(removed):
        writer.writerow([featurenames[i], absavgs[i], devs[i],features[i]])

#Plot Std Dev vs Avgs

def onpick3(event):
    ind = event.ind
    print 'onpick3 scatter:', ind, np.take(avgs,ind), np.take(devs,ind), np.take(np.asarray(featurenames),ind)

fig = plt.figure(figsize=(7,5))

plt.plot(absavgs, devs,'wo',linestyle='none', picker=5)
for feature in featurelist.keys():
    mask = [i for i, x in enumerate(features) if x == featurelist[feature]]
    plt.plot(absavgs[mask], devs[mask], linestyle='none', marker='o',label=feature)

plt.legend(numpoints=1)
plt.title('Robust Features for ' + title)
plt.xlabel('ABS(AVG)')
plt.ylabel('STD-DEV')
fig.canvas.mpl_connect('pick_event', onpick3)
plt.show()
