#!/usr/bin/env python3
# coding: utf-8

"""
ISODATAKit for ISODATA-python
Author:     Lucka
Version:    0.1.3
License:    MIT
"""

from PIL import Image
import numpy
import math
import random

# Class
class Pixel:
    """Pixel"""
    def __init__(self, initX: int, initY: int, initColor):
        self.x = initX
        self.y = initY
        self.color = initColor

class Cluster:
    """Cluster in Gray"""
    def __init__(self, initCenter):
        self.center = initCenter
        self.pixelList = []

class ClusterPair:
    """Cluster Pair"""
    def __init__(self, initClusterAIndex: int, initClusterBIndex: int, initDistance):
        self.clusterAIndex = initClusterAIndex
        self.clusterBIndex = initClusterBIndex
        self.distance = initDistance

# Functions

# Gray

def doISODATAGray(image, K: int, TN: int, TS: float, TC:int, L: int, I: int) -> Image.Image:
    imgArray = numpy.array(image)
    imgX, imgY = numpy.shape(imgArray)
    clusterList = []
    # Generate K cluster centers randomly
    for i in range(0, K):
        randomX = random.randint(0, imgX - 1)
        randomY = random.randint(0, imgY - 1)
        clusterList.append(Cluster(imgArray[randomX, randomY]))

    # Iteration
    iterationCount = 0
    while True:
        iterationCount += 1

        # Clear the pixel lists of all clusters
        for cluster in clusterList:
            cluster.pixelList.clear()
        print("------")
        print("Iteration: {0}".format(iterationCount))

        # Classify all pixels into clusters
        print("Classifying...", end = '', flush = True)
        for row in range(0, imgX):
            for col in range(0, imgY):
                targetClusterIndex = 0
                targetClusterDistance = abs(int(imgArray[row, col]) - int(clusterList[0].center))
                # Classify
                for i in range(0, len(clusterList)):
                    currentDistance = abs(int(imgArray[row, col]) - int(clusterList[i].center))
                    if currentDistance < targetClusterDistance:
                        targetClusterDistance = currentDistance
                        targetClusterIndex = i
                clusterList[targetClusterIndex].pixelList.append(Pixel(row, col, imgArray[row, col]))
        print(" Finished.")

        # Recalculate the centers
        print("Recalculating the centers...", end = '', flush = True)
        for cluster in clusterList:
            if len(cluster.pixelList) == 0:
                continue
            sum = 0.0
            for pixel in cluster.pixelList:
                sum += int(pixel.color)
            cluster.center = round(sum / len(cluster.pixelList))
        print(" Finished.")

        # The last iteration only classifies and recalculates the centers
        if iterationCount >= I:
            break

        # Calculate the average distance and the standard deviation of each cluster
        print("Preparing for Merging and Spliting...", end = '', flush = True)
        aveDistanceList = []
        sdList = []
        sumDistanceAll = 0.0
        for cluster in clusterList:
            currentSumDistance = 0.0
            currentSumSquare = 0.0
            for pixel in cluster.pixelList:
                currentSumDistance += abs(int(pixel.color) - int(cluster.center))
                currentSumSquare += (int(pixel.color) - int(cluster.center)) ** 2
            count = len(cluster.pixelList)
            aveDistanceList.append(currentSumDistance / count if count > 0 else 0.0)
            sdList.append(math.sqrt(currentSumSquare / (count - 1)) if count > 1 else 0.0)
            sumDistanceAll += currentSumDistance
        aveDistanceAll = float(sumDistanceAll) / (imgX * imgY)
        print(" Finished.")

        # Discard the clusters with fewer than TN patterns
        keepList = [len(cluster.pixelList) >= TN for cluster in clusterList]
        print("TN checking: {0} clusters discarded.".format(keepList.count(False)))
        clusterList = [cluster for cluster, keep in zip(clusterList, keepList) if keep]
        aveDistanceList = [value for value, keep in zip(aveDistanceList, keepList) if keep]
        sdList = [value for value, keep in zip(sdList, keepList) if keep]

        numberOfClusters = len(clusterList)
        if (numberOfClusters <= K / 2) or not (iterationCount % 2 == 0 or numberOfClusters >= K * 2):
            # Split
            print("Split:", end = '', flush = True)
            beforeCount = numberOfClusters
            for i in range(len(clusterList) - 1, -1, -1):
                if (sdList[i] > TS) and ((aveDistanceList[i] > aveDistanceAll and len(clusterList[i].pixelList) > 2 * (TN + 1)) or (numberOfClusters <= K / 2)):
                    # The offset is +1 / -1, as in the paper
                    clusterList.append(Cluster(int(clusterList[i].center) + 1))
                    clusterList.append(Cluster(int(clusterList[i].center) - 1))
                    clusterList.pop(i)
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))
        else:
            # Merge
            print("Merge:", end = '', flush = True)
            beforeCount = numberOfClusters
            clusterPairList = []
            for i in range(0, len(clusterList)):
                for j in range(0, i):
                    currentDistance = abs(int(clusterList[i].center) - int(clusterList[j].center))
                    if currentDistance < TC:
                        clusterPairList.append(ClusterPair(i, j, currentDistance))

            # Only the L closest pairs are considered
            clusterPairListSorted = sorted(clusterPairList, key = lambda clusterPair: clusterPair.distance)[:L]
            newClusterCenterList = []
            mergedClusterIndexList = []
            for clusterPair in clusterPairListSorted:
                if clusterPair.clusterAIndex in mergedClusterIndexList or clusterPair.clusterBIndex in mergedClusterIndexList:
                    continue
                nA = len(clusterList[clusterPair.clusterAIndex].pixelList)
                nB = len(clusterList[clusterPair.clusterBIndex].pixelList)
                newCenter = int((nA * float(clusterList[clusterPair.clusterAIndex].center) + nB * float(clusterList[clusterPair.clusterBIndex].center)) / (nA + nB))
                newClusterCenterList.append(newCenter)
                mergedClusterIndexList.append(clusterPair.clusterAIndex)
                mergedClusterIndexList.append(clusterPair.clusterBIndex)
            for index in sorted(mergedClusterIndexList, reverse = True):
                clusterList.pop(index)
            for center in newClusterCenterList:
                clusterList.append(Cluster(center))
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))

    # Generate the new image martrix
    print("Over")
    print("Classified to {0} kinds.".format(len(clusterList)))
    newImgArray = numpy.zeros((imgX, imgY), dtype = numpy.uint8)
    for cluster in clusterList:
        for pixel in cluster.pixelList:
            newImgArray[pixel.x, pixel.y] = int(cluster.center)

    return Image.fromarray(newImgArray, mode = "L")

# RGB
def distanceBetween(colorA, colorB) -> float:
    return math.sqrt(sum((int(colorA[j]) - int(colorB[j])) ** 2 for j in range(3)))

def doISODATARGB(image, K: int, TN: int, TS: float, TC:int, L: int, I: int) -> Image.Image:
    imgArray = numpy.array(image)
    imgY, imgX = image.size
    clusterList = []
    # Generate K cluster centers randomly
    for i in range(0, K):
        randomX = random.randint(0, imgX - 1)
        randomY = random.randint(0, imgY - 1)
        clusterList.append(Cluster(numpy.array([imgArray[randomX, randomY, 0],
                                                imgArray[randomX, randomY, 1],
                                                imgArray[randomX, randomY, 2]],
                                                dtype = numpy.uint8)))

    # Iteration
    iterationCount = 0
    while True:
        iterationCount += 1

        # Clear the pixel lists of all clusters
        for cluster in clusterList:
            cluster.pixelList.clear()
        print("------")
        print("Iteration: {0}".format(iterationCount))

        # Classify all pixels into clusters
        print("Classifying...", end = '', flush = True)
        for row in range(0, imgX):
            for col in range(0, imgY):
                targetClusterIndex = 0
                targetClusterDistance = distanceBetween(imgArray[row, col], clusterList[0].center)
                # Classify
                for i in range(1, len(clusterList)):
                    currentDistance = distanceBetween(imgArray[row, col], clusterList[i].center)
                    if currentDistance < targetClusterDistance:
                        targetClusterDistance = currentDistance
                        targetClusterIndex = i
                clusterList[targetClusterIndex].pixelList.append(Pixel(row, col, imgArray[row, col]))
        print(" Finished.")

        # Recalculate the centers
        print("Recalculating the centers...", end = '', flush = True)
        for cluster in clusterList:
            if len(cluster.pixelList) == 0:
                continue
            sumR = 0.0
            sumG = 0.0
            sumB = 0.0
            for pixel in cluster.pixelList:
                sumR += int(pixel.color[0])
                sumG += int(pixel.color[1])
                sumB += int(pixel.color[2])
            aveR = round(sumR / len(cluster.pixelList))
            aveG = round(sumG / len(cluster.pixelList))
            aveB = round(sumB / len(cluster.pixelList))
            cluster.center = numpy.array([aveR, aveG, aveB], dtype = numpy.uint8)
        print(" Finished.")

        # The last iteration only classifies and recalculates the centers
        if iterationCount >= I:
            break

        # Calculate the average distance and the standard deviation of each cluster
        print("Preparing for Merging and Spliting...", end = '', flush = True)
        aveDistanceList = []
        sdList = []
        sumDistanceAll = 0.0
        for cluster in clusterList:
            currentSumDistance = 0.0
            currentSumSquare = [0.0, 0.0, 0.0]
            for pixel in cluster.pixelList:
                currentSumDistance += distanceBetween(pixel.color, cluster.center)
                for j in range(3):
                    currentSumSquare[j] += (int(pixel.color[j]) - int(cluster.center[j])) ** 2
            count = len(cluster.pixelList)
            aveDistanceList.append(currentSumDistance / count if count > 0 else 0.0)
            sdList.append([math.sqrt(square / (count - 1)) if count > 1 else 0.0 for square in currentSumSquare])
            sumDistanceAll += currentSumDistance
        aveDistanceAll = float(sumDistanceAll) / (imgX * imgY)
        print(" Finished.")

        # Discard the clusters with fewer than TN patterns
        keepList = [len(cluster.pixelList) >= TN for cluster in clusterList]
        print("TN checking: {0} clusters discarded.".format(keepList.count(False)))
        clusterList = [cluster for cluster, keep in zip(clusterList, keepList) if keep]
        aveDistanceList = [value for value, keep in zip(aveDistanceList, keepList) if keep]
        sdList = [value for value, keep in zip(sdList, keepList) if keep]

        numberOfClusters = len(clusterList)
        if (numberOfClusters <= K / 2) or not (iterationCount % 2 == 0 or numberOfClusters >= K * 2):
            # Split
            print("Split:", end = '', flush = True)
            beforeCount = numberOfClusters
            for i in range(len(clusterList) - 1, -1, -1):
                maxSD = max(sdList[i])
                # Split along the component with the largest standard deviation
                k = sdList[i].index(maxSD)
                if (maxSD > TS) and ((aveDistanceList[i] > aveDistanceAll and len(clusterList[i].pixelList) > 2 * (TN + 1)) or (numberOfClusters <= K / 2)):
                    # The offset is +1 / -1 in component k, as in the paper
                    plusCenter = [int(value) for value in clusterList[i].center]
                    minusCenter = list(plusCenter)
                    plusCenter[k] += 1
                    minusCenter[k] -= 1
                    clusterList.append(Cluster(numpy.array(plusCenter, dtype = numpy.uint8)))
                    clusterList.append(Cluster(numpy.array(minusCenter, dtype = numpy.uint8)))
                    clusterList.pop(i)
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))
        else:
            # Merge
            print("Merge:", end = '', flush = True)
            beforeCount = numberOfClusters
            clusterPairList = []
            for i in range(0, len(clusterList)):
                for j in range(0, i):
                    currentDistance = distanceBetween(clusterList[i].center, clusterList[j].center)
                    if currentDistance < TC:
                        clusterPairList.append(ClusterPair(i, j, currentDistance))

            # Only the L closest pairs are considered
            clusterPairListSorted = sorted(clusterPairList, key = lambda clusterPair: clusterPair.distance)[:L]
            newClusterCenterList = []
            mergedClusterIndexList = []
            for clusterPair in clusterPairListSorted:
                if clusterPair.clusterAIndex in mergedClusterIndexList or clusterPair.clusterBIndex in mergedClusterIndexList:
                    continue
                nA = len(clusterList[clusterPair.clusterAIndex].pixelList)
                nB = len(clusterList[clusterPair.clusterBIndex].pixelList)
                newCenter = [int((nA * float(clusterList[clusterPair.clusterAIndex].center[j]) + nB * float(clusterList[clusterPair.clusterBIndex].center[j])) / (nA + nB)) for j in range(3)]
                newClusterCenterList.append(newCenter)
                mergedClusterIndexList.append(clusterPair.clusterAIndex)
                mergedClusterIndexList.append(clusterPair.clusterBIndex)
            for index in sorted(mergedClusterIndexList, reverse = True):
                clusterList.pop(index)
            for center in newClusterCenterList:
                clusterList.append(Cluster(numpy.array(center, dtype = numpy.uint8)))
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))

    # Generate the new image martrix
    print("Over")
    print("Classified to {0} kinds.".format(len(clusterList)))
    newImgArray = numpy.zeros((imgX, imgY, 3), dtype = numpy.uint8)
    for cluster in clusterList:
        for pixel in cluster.pixelList:
            newImgArray[pixel.x, pixel.y, 0] = int(cluster.center[0])
            newImgArray[pixel.x, pixel.y, 1] = int(cluster.center[1])
            newImgArray[pixel.x, pixel.y, 2] = int(cluster.center[2])

    return Image.fromarray(newImgArray, mode = "RGB")

if __name__ == '__main__':
    print("ERROR: Pleas don not run the module directly.")
