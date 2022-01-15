from math import sqrt

class SilhouetteCoefficient:
    def __init__(self, clusters, data_norm):
        self.clusters = clusters
        self.data_norm = data_norm
        self.score_si = []
        self.cohesion = []
        self.separation = []
        self.avg_score = 0.0
        self.calculate()

    def calculate(self):
        ai= []
        bi = []
        si_score = []
        for i in range(len(self.data_norm[0])):
            dis_inter = []
            dis_intra = []
            dict_inter = { c:[] for c in range(max(self.clusters)+1) if c != self.clusters[i]}
            for j in range(len(self.data_norm[0])): 
                if self.clusters[i] == self.clusters[j] and i != j:
                    temp_k = 0
                    for k in range(len(self.data_norm)):
                        temp_k += (self.data_norm[k][i]-self.data_norm[k][j])**2
                    dis_intra.append(sqrt(temp_k))
                elif self.clusters[i] != self.clusters[j] and i != j:
                    temp_k = 0
                    for k in range(len(self.data_norm)):
                        temp_k += (self.data_norm[k][i]-self.data_norm[k][j])**2
                    dict_inter[self.clusters[j]].append(sqrt(temp_k))
            
            for value in dict_inter.values():
                dis_inter.append(sum(value)/len(value))
    
            bi.append(min(dis_inter))
            if len(dis_intra)>0: 
                ai.append(sum(dis_intra)/len(dis_intra))
                si_score.append((bi[i]-ai[i])/max(bi[i],ai[i]))
            else: 
                ai.append(0)
                si_score.append(0)
        
        self.score_si = si_score
        self.cohesion = ai
        self.separation = bi
        self.avg_score = sum(si_score)/len(si_score)