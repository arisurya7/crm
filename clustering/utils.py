import builtins
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from sklearn.decomposition import PCA

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,5))
    plt.title('Sample Data')
    plt.plot(x,y)
    plt.xticks(rotation=45)
    plt.xlabel('item')
    plt.ylabel('value')
    plt.tight_layout()
    graph = get_graph()
    return graph

def threedim_scatter_plot(x=[],y=[],z=[],data_param=[],labels=[]):
    colors= ['red', 'green', 'blue', 'yellow', 'orange', 'black']
    plt.switch_backend('AGG')
    plt.figure()
    ax = plt.axes(projection='3d')
    if len(x)>0 and len(y)>0 and len(z)>0:
        ax.scatter(x,y,z, color='red')
    else:
        data=[] 
        if len(data_param)==3:
            for i in range(max(labels)+1):
                cluster=[[],[],[]]
                for j in range(len(data_param[0])):
                    if i == labels[j]:
                        for k in range(len(data_param)):
                            cluster[k].append(data_param[k][j])  
                data.append(cluster)
        else:
            data_tansform = list(map(list, zip(*data_param)))
            data_pca = PCA(n_components=3).fit_transform(data_tansform)
            for i in range(max(labels)+1):
                cluster=[[],[],[]]
                for j in range(len(data_pca)):
                    if i == labels[j]:
                        cluster[0].append(data_pca[j][0])
                        cluster[1].append(data_pca[j][1])
                        cluster[2].append(data_pca[j][2])
                data.append(cluster)

        for i,cluster in enumerate(data):
            ax.scatter(cluster[0],cluster[1], cluster[2], color=colors[i], label='cluster '+str(i+1))
            if len(data_param)==3:
                ax.set_xlabel('Recency')
                ax.set_ylabel('Frequency')
                ax.set_zlabel('Monetary')
            else:
                ax.set_xlabel('PC 1')
                ax.set_ylabel('PC 2')
                ax.set_zlabel('PC 3')
            ax.set_title('3D Scatter Plot Cluster')
            ax.legend(title='Cluster Data')

    graph = get_graph()
    return graph

def silhouette_bar(score_si, labels):
    colors= ['red', 'green', 'blue', 'yellow', 'orange', 'black']
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()
    y_upper = y_lower = 0
    for i in range(max(labels)+1):
        cluster_sc = [score_si[k] for k, v in enumerate(labels) if v ==i]
        cluster_sc.sort()
        
        y_upper += len(cluster_sc)
        ax.barh(range(y_lower,y_upper), cluster_sc,height =1, color=colors[i], label='cluster '+str(i+1))
        ax.text(-0.03,(y_lower+y_upper)/2,str(i+1))
        y_lower += len(cluster_sc)
        
        # Get the average silhouette score 
        avg_score = sum(score_si)/len(score_si)
        ax.axvline(avg_score,linestyle ='--', linewidth =2,color = 'green')
        ax.set_yticks([])
        ax.set_xlim([-0.1, 1])
        ax.set_xlabel('Silhouette coefficient values')
        ax.set_ylabel('Cluster labels')
        ax.legend(title='Cluster Data')
        ax.set_title('Silhouette plot for the various clusters')

    graph = get_graph()
    return graph

def silhouette_plot(x, y):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()
    ax.set_ylim(-1,1)
    ax.set_xlim(min(x)-0.5,max(x)+0.5)
    plt.plot(x,y)
    plt.title('Silhouette Coefficient K Cluster')
    plt.ylabel('Score')
    plt.xlabel('Number k cluster')
    for i,j in zip(x,y):
        ax.annotate(str(j),xy=(i,j))
    
    graph = get_graph()
    return graph