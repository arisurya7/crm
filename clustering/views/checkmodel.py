def checkTypeModel(attribute, point_centroid, data_compare):
    if attribute == 'L':
        return 'L↑' if point_centroid > sum(data_compare)/len(data_compare) else 'L↓'
    elif attribute == 'R':
        return 'R↑' if point_centroid > sum(data_compare)/len(data_compare) else 'R↓'
    elif attribute == 'F':
        return 'F↑' if point_centroid > sum(data_compare)/len(data_compare) else 'F↓'
    elif attribute == 'M':
        return 'M↑' if point_centroid > sum(data_compare)/len(data_compare) else 'M↓'
    else:
        return 'Wrong'

def checkSilhouetteStructure(si):
    if si <=0.25:
        return 'No Structure'
    elif si > 0.25 and si <=0.5:
        return 'Weak Structure'
    elif si > 0.5 and si <=0.7:
        return 'Medium Structure'
    elif si > 0.7 and si <=1:
        return 'Strong Structure'
    else:
        return ''