from math import sqrt
import numpy as np

class Topsis:
    def __init__(self, data, benefit, cost, weight=[], alternative=[], criteria=[]):
        self.data = data
        self.weight = [1 for i in data.keys()] if len(weight)==0 else weight
        self.benefit = benefit
        self.cost = cost
        self.alternative = ['a'+str(i) for i in range(len(data[benefit[0]]))] if len(alternative)==0 else alternative
        self.criteria = [i for i in data.keys()] if len(criteria)==0 else criteria
        self.top_pref = ''
        self.low_pref = ''
        self.matrixNormalization()
        self.weightMatrixNorm()
        self.matrixIdealSolution()
        self.distanceAlternative()
        self.preferensi()

    def matrixNormalization(self):        
        square_root = [sqrt(sum(list(map(lambda x : x**2, i)))) for i in self.data.values()]
        matrixNorm = { self.criteria[i]:list(map(lambda x : x/square_root[i], self.data[self.criteria[i]])) for i in range(len(self.criteria))}
        return matrixNorm
    
    def weightMatrixNorm(self):
        matrixWeight = self.matrixNormalization()
        for i in range(len(self.criteria)):
            matrixWeight[self.criteria[i]] = list(map(lambda x : x * self.weight[i], matrixWeight[self.criteria[i]]))
        return matrixWeight
    
    def matrixIdealSolution(self):
        matrixIdeal = {}
        matrixIdeal['aplus'] = [ max(value) if key in self.benefit else min(value) for key, value in self.weightMatrixNorm().items()] 
        matrixIdeal['amin'] = [ max(value) if key in self.cost else min(value) for key, value in self.weightMatrixNorm().items()] 
        return matrixIdeal
    
    def distanceAlternative(self):
        distanceAlter = {}
        weightMatrixNorm = np.array(list(map(list, zip(*[data for data in self.weightMatrixNorm().values()]))))
        distanceAlter['d+'] = list(np.sqrt(((weightMatrixNorm - np.array(self.matrixIdealSolution()['aplus']))**2).sum(axis=1)))
        distanceAlter['d-'] = list(np.sqrt(((weightMatrixNorm - np.array(self.matrixIdealSolution()['amin']))**2).sum(axis=1)))
        return distanceAlter
    
    def calculate_rank(self,vector):
        array = np.array(vector)
        sorted_indices = np.argsort(-array)
        ranks = np.empty_like(sorted_indices)
        ranks[sorted_indices] = np.arange(len(array))
        return list(ranks+1)
    
    def preferensi(self):
        da = self.distanceAlternative()
        vi = [da['d-'][i] / (da['d-'][i] + da['d+'][i]) for i in range(len(self.alternative))]
        self.top_pref = self.alternative[vi.index(max(vi))]
        self.low_pref = self.alternative[vi.index(min(vi))]
        rank = self.calculate_rank(vi)
        return list(zip(self.alternative,vi,rank))