from math import sqrt

class Topsis:
    def __init__(self, data, weight, benefit, cost, alternative=[], criteria=[]):
        self.data = data
        self.weight = weight
        self.benefit = benefit
        self.cost = cost
        self.alternative = ['a'+str(i) for i in range(len(data[benefit[0]]))] if len(alternative)==0 else alternative
        self.criteria = [i for i in data.keys()] if len(criteria)==0 else criteria
        self.top_pref = ''
        self.low_pref = ''
        self.result = []
        self.preferensi()
    
    def matrixNormalization(self):        
        #get square root of every criteria
        square_root = [sqrt(sum(list(map(lambda x : x**2, i)))) for i in self.data.values()]
        #calculate matrix normalization
        matrixNorm = { self.criteria[i]:list(map(lambda x : x/square_root[i], self.data[self.criteria[i]])) for i in range(len(self.criteria))}
        return matrixNorm
    
    def weightMatrixNorm(self):
        matrixWeight = self.matrixNormalization()
        for i in range(len(self.criteria)):
            matrixWeight[self.criteria[i]] = list(map(lambda x : x * self.weight[i], matrixWeight[self.criteria[i]]))
        return matrixWeight
    
    def matrixIdealSolution(self):
        matrixWeight = self.weightMatrixNorm()
        matrixIdeal = {}
        matrixIdeal['a+'] = [ max(value) if key in self.benefit else min(value) for key, value in matrixWeight.items()] 
        matrixIdeal['a-'] = [ max(value) if key in self.cost else min(value) for key, value in matrixWeight.items()] 
        return matrixIdeal
    
    def distanceAlternative(self):
        matrixWeight = self.weightMatrixNorm()
        matrixIdeal = self.matrixIdealSolution()
        distanceAlter = {}
        
        tda=[]
        for i in range(len(self.alternative)):
            lst = [value[i] for value in matrixWeight.values()]
            diff=[]
            for j in range(len(self.criteria)):
                diff.append((matrixIdeal['a+'][j]-lst[j])**2)
            tda.append(sqrt(sum(diff)))            
        distanceAlter['d+'] = tda
        
        tda=[]
        for i in range(len(self.alternative)):
            lst = [value[i] for value in matrixWeight.values()]
            diff=[]
            for j in range(len(self.criteria)):
                diff.append((lst[j]-matrixIdeal['a-'][j])**2)
            tda.append(sqrt(sum(diff)))            
        distanceAlter['d-'] = tda
        
        return distanceAlter
    
    def preferensi(self):
        da = self.distanceAlternative()
        vi = [da['d-'][i] / (da['d-'][i] + da['d+'][i]) for i in range(len(self.alternative))]
        self.top_pref = self.alternative[vi.index(max(vi))]
        self.low_pref = self.alternative[vi.index(min(vi))]
        self.result = list(zip(self.alternative,vi))