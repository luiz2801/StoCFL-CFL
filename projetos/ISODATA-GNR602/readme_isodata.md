# ISODATA_Classifier
Python Based Implementation of the ISODATA Classifier with GUI enabled (Repository is not complete and will be updated soon.)

## GNR-602 Advanced Image Processing
### Group - 68


We have taken Indian Pines dataset. This scene was gathered by AVIRIS sensor over the Indian Pines test site in
North-western Indiana and consists of 145´145 pixels and 224 spectral reflectance bands in the wavelength range 
0.4–2.5 10-6 meters. The Indian Pines scene contains two-thirds agriculture, and one-third forest or other natural 
perennial vegetation. There are two major dual lane highways, a rail line, as well as some low density housing,
other built structures, and smaller roads.

------------------------------------------------------------------------------------------------------------------

The dataset is downloaded on system which can be imported from local directory to run the code.

------------------------------------------------------------------------------------------------------------------
## Implementation details

* Language : python 3
* IDE used : VS code
* Libraries used : numpy, matplotlib.pyplot, tqdm, scipy.io (loadmat)


## Steps to run the program -

1. Execute and compile "Executable.py" which will call "GUI.py" which will further call "Classifier.py" to run the
program.

```
$ python Executable.py
```

-------------------------------------------------------------------------------------------------------------------

Parameters chosen - 
```
#desired_number_of_clusters 
K = 16

#Maximum number of iterations
I = 100

#Maximum clusters pair mergers
P = 1

#Number of Clusters starting pair
k = 100

#Threshold's cluster size 
ThresholdClusterSize = 10

#Threshold for Intraclass standard deviation 
ThresholSD = 100

#Threshold for Pairwise Distances
ThresholdDistance =2000

#Threshold for Consecutive Iteration Change in Cluster
ThresholdClusterChange = 0.05
```
