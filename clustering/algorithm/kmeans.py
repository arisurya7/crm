from math import sqrt
from random import sample
from random import randint
import numpy as np

class Kmeans:
    def __init__(self, data, k, centroid_init='kplusplus', max_iter=30):
        self.k = k
        self.centroid_init = centroid_init
        self.data = data
        self.max_iter = max_iter

    def calculate(self):
        centroids = self.init_centroid()
        data_cluster = self.data.copy()
        iter = 0
        data_distance = [0]
        data_distance_new = [1]
        while data_distance[-1]!=data_distance_new[-1] and iter < self.max_iter:
            data_distance = self.calculate_distance(data_cluster, centroids)
            centroids = self.update_centroid(centroids, data_cluster, data_distance)
            data_distance_new = self.calculate_distance(data_cluster, centroids)
            iter=iter+1
        return {'data_distance':data_distance_new, 'clusters':data_distance_new[-1], 'centroids':centroids}

    def calculate_distance(self, data_cluster, centroids):
        data_distance = []
        for centroid in np.array(centroids):
            dis = np.sqrt(((np.array(data_cluster).transpose() - centroid)**2).sum(axis=1))
            data_distance.append(list(dis))
        labels = [ list(data).index(data.min(axis=0)) for data in np.array(data_distance).transpose()]
        data_distance.append(labels)
        return data_distance
    
    def update_centroid(self, centroids, data_cluster, distance):
        for d,centroid in enumerate(centroids):
            for i,c in enumerate(centroid):
                temp_c = []
                for j in range(len(distance[0])): 
                    if distance[-1][j] == d:
                        temp_c.append(data_cluster[i][j])
                centroids[d][i] = sum(temp_c)/len(temp_c)
        return centroids

    def init_centroid(self):
        if(self.centroid_init == 'random'):
            index_init_centroid = sample(range(0, len(self.data[0])),self.k)
        elif (self.centroid_init == 'kplusplus'):
            index_init_centroid = self.kplusplus(self.data, self.k)        
        data_cluster = list(map(list, zip(*self.data))) 
        return [data_cluster[i] for i in index_init_centroid]

    def kplusplus(self, data, k):
        index_centroid = []
        index_centroid.append(randint(0, len(data[0])-1))
        for r in range(k-1):
            dis = []
            for c in index_centroid:
                rs = list(((np.array(data).transpose() - np.array(data).transpose()[c])**2).sum(axis=1))
                dis.append(rs)
            min_dis = list(np.array(dis).min(axis=0))
            max_prob = min_dis.index(max(min_dis))
            index_centroid.append(max_prob)
        return index_centroid
