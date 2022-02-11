
class AhpWeight:
    def __init__(self, data_input, criteria):
        self.data_input = data_input
        self.criteria = criteria
        self.random_index = {1:0, 2:0, 3:0.58, 4:0.9, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
        self.comparison_matrix = []
        self.norm_matrix = []
        self.weight_priority = []
        self.final_weight = {}
        self.eigen_vector = []
        self.max_eigen_vector = 0.0
        self.consintency_index = 0.0
        self.consistency_ratio = 0.0
        self.calculate()
        

    def calculate(self):
        sum_columns = [0 for i in range(len(self.criteria))]      
        for i in range(len(self.criteria)):
            temp=[]
            for j in range(len(self.criteria)):
                if i == j: temp.append(1)
                elif str(i)+str(j) in self.data_input.keys():
                    temp.append(self.data_input[str(i)+str(j)])
                else:
                    temp.append(1/self.data_input[str(j)+str(i)])
                sum_columns[j]+=temp[j]
            self.comparison_matrix.append(temp)
    
        for i in range(len(self.comparison_matrix)):
            temp=[]
            for j in range(len(self.comparison_matrix)):
                temp.append(self.comparison_matrix[i][j]/sum_columns[j])
            self.weight_priority.append(sum(temp)/len(temp))
            self.norm_matrix.append(temp)
        
        temp_wp = [[i] for i in self.weight_priority]
        aw = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*temp_wp)] for X_row in self.comparison_matrix]
        self.eigen_vector = [ aw[i][0]/temp_wp[i][0] for i in range(len(aw))]
        self.max_eigen_vector = sum(self.eigen_vector)/len(self.eigen_vector)
        self.consintency_index = (self.max_eigen_vector-len(self.criteria))/(len(self.criteria)-1)
        self.consistency_ratio = self.consintency_index/self.random_index[len(self.criteria)]
        
        if self.consistency_ratio < 0.1:
            self.final_weight = { self.criteria[i]:self.weight_priority[i] for i in range(len(self.criteria))}
       
        