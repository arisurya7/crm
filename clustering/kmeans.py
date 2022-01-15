from math import sqrt
from random import sample
from random import randint

class Kmeans:
    def __init__(self, data, k, max_iter=30):
        self.k = k
        self.data = data
        self.max_iter = max_iter


    def calculate(self):
        centroids = self.init_centroid()
        data_cluster = self.data.copy()
        iter = 0
        data_distance = [0]
        data_distance_new = [1]
        while data_distance[-1]!=data_distance_new[-1] or iter > self.max_iter:
            data_distance = self.calculate_distance(data_cluster, centroids)
            centroids = self.update_centroid(centroids, data_cluster, data_distance)
            data_distance_new = self.calculate_distance(data_cluster, centroids)
            iter=iter+1
        return {'data_distance':data_distance_new, 'clusters':data_distance_new[-1], 'centroids':centroids}


    def calculate_distance(self, data_cluster, centroids):
        data_distance = [[] for i in range(len(centroids)+1)]
        for j in range(len(data_cluster[0])):
            temp_c =[]
            for d, centroid in enumerate(centroids):
                temp_d = 0
                for i,c in enumerate(centroid):
                    temp_d += (data_cluster[i][j]-c)**2
                dis = sqrt(temp_d)
                temp_c.append(dis)
                data_distance[d].append(dis)
            data_distance[-1].append(temp_c.index(min(temp_c)))
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
        # Init centroid from random index
        # index_init_centroid = sample(range(0, len(self.data[0])),self.k)
        # Init centroid from kmeans++
        index_init_centroid = self.kplusplus(self.data, self.k)

        centroids = []
        for j in range(0, len(self.data[0])):
            centroid = []
            for i in range(0, len(self.data)):
                if j in index_init_centroid:
                    centroid.append(self.data[i][j])
                else:
                    break
            if(len(centroid)>0):
                centroids.append(centroid)
        return centroids

    def kplusplus(self, data, k):
        first_centroid = randint(0, len(data[0])-1)
        index_centroid = []
        index_centroid.append(first_centroid)
        for r in range(k-1):
            min_dis = []
            for j in range(len(data[0])):
                dis=[]
                for c in index_centroid:
                    temp_d=0
                    for i in range(len(data)):
                        temp_d += (data[i][c]-data[i][j])**2
                    dis.append(temp_d)
                min_dis.append(min(dis))
            max_probabilitas = min_dis.index(max(min_dis))
            index_centroid.append(max_probabilitas)
        return index_centroid
