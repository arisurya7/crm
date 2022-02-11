class MinMaxNorm:
    def __init__(self, data):
        self.data = data
    def calculate(self):
        data_norm = self.data.copy()
        for i, da in enumerate(data_norm):
            maxi = max(da)
            mini = min(da)
            for j, d in enumerate(da):
                data_norm[i][j] = (d-mini)/(maxi-mini)
        return data_norm