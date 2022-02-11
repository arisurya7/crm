from math import sqrt

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
        self.result = []
        self.matrixNorm = []
        self.matrixIdeal = []
        self.distanceAlter = []
        self.preferensi()
    
    def matrixNormalization(self):        
        #get square root of every criteria
        square_root = [sqrt(sum(list(map(lambda x : x**2, i)))) for i in self.data.values()]
        #calculate matrix normalization
        matrixNorm = { self.criteria[i]:list(map(lambda x : x/square_root[i], self.data[self.criteria[i]])) for i in range(len(self.criteria))}
        return matrixNorm
    
    def weightMatrixNorm(self):
        self.matrixNorm = self.matrixNormalization()
        matrixWeight = self.matrixNorm.copy()
        for i in range(len(self.criteria)):
            matrixWeight[self.criteria[i]] = list(map(lambda x : x * self.weight[i], matrixWeight[self.criteria[i]]))
        return matrixWeight
    
    def matrixIdealSolution(self):
        matrixWeight = self.weightMatrixNorm()
        matrixIdeal = {}
        matrixIdeal['aplus'] = [ max(value) if key in self.benefit else min(value) for key, value in matrixWeight.items()] 
        matrixIdeal['amin'] = [ max(value) if key in self.cost else min(value) for key, value in matrixWeight.items()] 
        self.matrixIdeal = matrixIdeal
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
                diff.append((matrixIdeal['aplus'][j]-lst[j])**2)
            tda.append(sqrt(sum(diff)))            
        distanceAlter['d+'] = tda
        
        tda=[]
        for i in range(len(self.alternative)):
            lst = [value[i] for value in matrixWeight.values()]
            diff=[]
            for j in range(len(self.criteria)):
                diff.append((lst[j]-matrixIdeal['amin'][j])**2)
            tda.append(sqrt(sum(diff)))            
        distanceAlter['d-'] = tda
        self.distanceAlter = distanceAlter
        return distanceAlter
    
    def calculate_rank(self,vector):
        a={}
        rank=1
        for num in sorted(vector, reverse=True):
            if num not in a:
                a[num]=rank
                rank=rank+1
        return[a[i] for i in vector]

    def preferensi(self):
        da = self.distanceAlternative()
        vi = [da['d-'][i] / (da['d-'][i] + da['d+'][i]) for i in range(len(self.alternative))]
        self.top_pref = self.alternative[vi.index(max(vi))]
        self.low_pref = self.alternative[vi.index(min(vi))]
        rank = self.calculate_rank(vi)
        self.result = list(zip(self.alternative,vi,rank))