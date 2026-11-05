import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from tqdm import tqdm
from PIL import Image
from sklearn.preprocessing import normalize

class Isodata_Classifier:
    def __init__(self,  PathToImage, PathToGroundTruth, DictKeyImage = 'indian_pines_corrected', DictKeyGroundTruth = 'indian_pines_gt', parameters = None, Dictionary_Keys = None):
        
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = {}
        
        #Desired Number Of Clusters
        self.K = self.parameters.get('K', 16)

        #Maximum Number Of Iterations
        self.I = self.parameters.get('I', 100)

        #Maximum Cluster Pair Merges That Can Be Performed
        self.P = self.parameters.get('P', 1)

        #Number Of Starting Clusters
        self.k = self.parameters.get('k', self.K)

        #Thresholds

        #Threshold Cluster Size [Cluster Dismissal Condition]
        self.ThresholdClusterSize = self.parameters.get('ThresholdClusterSize', 10)

        #Threshold For Intraclass Standard Deviation [Cluster Split Condition]
        self.ThresholdSD = self.parameters.get('ThresholSD', 1)

        #Threshold For Pairwise Distances [Clusters Join Condition]
        self.ThresholdDistance = self.parameters.get('ThresholdDistance', 1)

        #Threshold For Consecutive Iteration Change In Cluster [Algorithm Termination Condition]
        self.ThresholdClusterChange = self.parameters.get('ThresholdClusterChange', 0.05)

        #Initialise Required Variables
        self.Read_Image(PathToImage, PathToGroundTruth, DictKeyImage, DictKeyGroundTruth)
        self.Build_Pixel_Data()
        self.Initialise_Means(Method = 'From Data')
        self.Initialise_Clusters()

    def Read_Image(self, PathToImage, PathToGroundTruth, DictKeyImage = 'indian_pines_corrected', DictKeyGroundTruth = 'indian_pines_gt'):

        self.Image = loadmat(PathToImage)[DictKeyImage]
        self.GroundTruth = loadmat(PathToGroundTruth)[DictKeyGroundTruth]
        print(self.Image.shape)
    
    def Build_Pixel_Data(self):
        self.PixelData = []
        
        self.X, self.Y, self.Channels = self.Image.shape
        for x in range(self.X):
            for y in range(self.Y):
                self.PixelData.append(self.Image[x, y, :])
        
        self.PixelData = np.array(self.PixelData)
        self.PixelData = normalize(self.PixelData)
    
    def Initialise_Means(self, Method = 'From Data'):
        if Method == 'Random':
            InitialMean = np.average(self.PixelData, axis = 0)
            self.ClusterMeans = []
            for i in range(self.k):
                self.ClusterMeans.append(InitialMean*np.random.rand(self.Channels))
            self.ClusterMeans = np.array(self.ClusterMeans)
        elif Method == 'From Data':
            self.ClusterMeans = self.PixelData[np.random.randint(0, 199, self.k)]
            
    def Initialise_Clusters(self):
        
        self.ClusterIndices = []

        for i in range(len(self.PixelData)):
            Distances = []
            
            for j in range(len(self.ClusterMeans)):
                Distances.append(self.Calculate_Distance(self.PixelData[i], self.ClusterMeans[j]))
            
            Distances = np.array(Distances)
            self.ClusterIndices.append(np.argmin(Distances))
        
        self.ClusterIndices = np.array(self.ClusterIndices)

    def Calculate_Distance(self, A, B):
        return np.sqrt(np.sum(np.square(A - B)))

    def Merge_Clusters(self, Cluster1Index, Cluster2Index):
        NewMean = (self.ClusterMeans[Cluster1Index]*self.ClusterMeans[Cluster1Index].shape[0]+self.ClusterMeans[Cluster2Index]*self.ClusterMeans[Cluster2Index].shape[0])/(self.ClusterMeans[Cluster1Index].shape[0] + self.ClusterMeans[Cluster2Index].shape[0])

        LastClusterMeans = self.ClusterMeans
        self.ClusterMeans = np.delete(self.ClusterMeans, [Cluster1Index, Cluster2Index], axis = 0)
        self.ClusterMeans = np.append(self.ClusterMeans, np.array([NewMean]), axis = 0)
        RemapIndices = {}

        for i in range(len(LastClusterMeans)):
            if i < Cluster1Index:
                if i < Cluster2Index:
                    RemapIndices[i] = i
                elif i > Cluster2Index:
                    RemapIndices[i] = i - 1
                else:
                    pass
            
            elif i > Cluster1Index:
                if i < Cluster2Index:
                    RemapIndices[i] = i - 1
                elif i > Cluster2Index:
                    RemapIndices[i] = i - 2
            
            else:
                pass

        RemapIndices[Cluster1Index] = len(self.ClusterMeans) - 1
        RemapIndices[Cluster2Index] = len(self.ClusterMeans) - 1
        
        for i in range(self.ClusterIndices.size):
            self.ClusterIndices[i] = RemapIndices[self.ClusterIndices[i]]
        
        self.LastClusterMeans = LastClusterMeans
        self.k = self.k - 1

    def Remove_Cluster(self, ClusterIndex):
        self.LastClusterMeans = self.ClusterMeans
        self.ClusterMeans = np.delete(self.ClusterMeans, ClusterIndex, axis = 0)
        RemapIndices = {}

        for i in range(len(self.LastClusterMeans)):
            if i < ClusterIndex:
                RemapIndices[i] = i
            elif i > ClusterIndex:
                RemapIndices[i] = i - 1
            else:
                pass

        RemapIndices[ClusterIndex] = -1

        for i in range(self.ClusterIndices.size):
            self.ClusterIndices[i] = RemapIndices[self.ClusterIndices[i]]
        
        self.k = self.k - 1
    
    def Split_Cluster(self, ClusterIndex):
        #Randomly Splitting Pixels in the Cluster to be split

        IndicesToBeSplit = self.ClusterIndices == ClusterIndex
        self.LastClusterMeans = self.ClusterMeans
        self.ClusterMeans = np.delete(self.ClusterMeans, ClusterIndex, axis = 0)

        RemapIndices = {}

        for i in range(len(self.LastClusterMeans)):
            if i < ClusterIndex:
                RemapIndices[i] = i
            elif i > ClusterIndex:
                RemapIndices[i] = i - 1
            else:
                pass
        RemapIndices[ClusterIndex] = -1

        for i in range(self.ClusterIndices.size):
            self.ClusterIndices[i] = RemapIndices[self.ClusterIndices[i]]
        
        Choices = [self.ClusterMeans.size, self.ClusterMeans.size + 1]
        
        self.ClusterIndices[IndicesToBeSplit] = np.random.choice(Choices, size = IndicesToBeSplit.sum())

        self.ClusterMeans = np.append(self.ClusterMeans, np.array([np.average(self.PixelData[self.ClusterIndices == Choices[0]], axis = 0)]), axis = 0)
        self.ClusterMeans = np.append(self.ClusterMeans, np.array([np.average(self.PixelData[self.ClusterIndices == Choices[1]], axis = 0)]), axis = 0)

        self.k = self.k + 1

    def Move_Cluster_Means(self):
        for i in range(len(self.ClusterMeans)):
            self.ClusterMeans[i] = np.average(self.PixelData[self.ClusterIndices == i], axis = 0)

    def Compute_Stats(self):
        self.DeltaJ = []
        
        for i in range(self.k):
            DataJ = self.PixelData[self.ClusterIndices == i]
            DataJ = DataJ - self.ClusterMeans[i]
            DataJ = np.sum(DataJ**2, axis = 1)
            DataJ = np.average(DataJ)
            self.DeltaJ.append(DataJ)
        self.DeltaJ = np.array(self.DeltaJ)
        self.Delta = np.sum([self.DeltaJ[i]*self.PixelData[self.ClusterIndices == i].shape[0] for i in range(self.k)])/(self.PixelData.shape[0])

        self.Vi = np.array(max([np.std(self.PixelData[self.ClusterIndices == i], axis = 0)]) for i in range(self.k))

    def Recompute_Cluster_Indices(self):
        self.ClusterIndices = []
        for i in range(len(self.PixelData)):
            Distances = []
            
            for j in range(len(self.ClusterMeans)):
                Distances.append(self.Calculate_Distance(self.PixelData[i], self.ClusterMeans[j]))
            
            Distances = np.array(Distances)
            self.ClusterIndices.append(np.argmin(Distances))
        
        self.ClusterIndices = np.array(self.ClusterIndices)
    
    def Cluster_Size_Check(self):
        IndicesToRemove = []

        for i in range(self.ClusterMeans.shape[0]):
            if self.ClusterIndices[self.ClusterIndices == i].shape[0] <= self.ThresholdClusterSize:
                IndicesToRemove.append(i)
        return IndicesToRemove
    
    def Compute_Pairwise_Distance(self):
        Distances = [[0]*self.k]*self.k
        for i in range(self.k):
            for j in range(i + 1, self.k):
                Distances[i][j] = self.Calculate_Distance(self.ClusterMeans[i], self.ClusterMeans[j])
        self.Distances = np.array(Distances)
        return np.unravel_index(np.argmax(self.Distances), self.Distances.shape)

    def Iterations(self):

        for iter in tqdm(range(self.I)):
            self.Recompute_Cluster_Indices()
            IndicesToRemove = np.array(self.Cluster_Size_Check())

            if IndicesToRemove.size > 0:
                self.Remove_Cluster(IndicesToRemove[0])
                continue

            self.Move_Cluster_Means()
            self.Compute_Stats()

            if np.any(self.DeltaJ - self.ThresholdDistance > 0):
                self.Split_Cluster(np.argmax(self.DeltaJ - self.ThresholdDistance))
                print(self.Delta)
                continue

            Index = self.Compute_Pairwise_Distance()

            if self.Distances[Index] > self.ThresholdDistance:
                self.Merge_Clusters(Index[0], Index[1])
                print(self.Delta)
                continue
            
    def plot_band(self, band_no):
        ax, fig = plt.subplots(figsize=(8,6))
        #band_no = np.random.randint(dataset.shape[2])
        plt.imshow(self.Image[:,:,band_no], cmap = 'jet')
        plt.title(f'Band-{band_no}', fontsize = 14)
        plt.axis('off')
        plt.colorbar()
        plt.show()

    def pixel_signature(self, pixel_location):
        bands = np.linspace(0, 199, 200)
        plt.plot(bands, self.Image[pixel_location[0], pixel_location[1]], '--')
        plt.title(f'Pixel Location: {pixel_location}, Ground Truth Class: {self.GroundTruth[pixel_location[0], pixel_location[1]]}')
        plt.xlabel('Band Number')
        plt.ylabel('Pixel Intensity')
        plt.show()

    def Save_Image(self, SavePath):
        ClassifiedImage = self.ClusterIndices.reshape(self.Image.shape[0:2])
        ImageToSave = Image.fromarray(ClassifiedImage)
        ImageToSave.save(SavePath)
