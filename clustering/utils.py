import matplotlib.pyplot as plt
import numpy as np
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

def threedim_scatter_plot(x=[],y=[],z=[],data_param=[],labels=[], title_scatter = '3D Scatter Plot Cluster'):
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
            ax.set_title(title_scatter)
            ax.legend(title='Cluster Data')

    graph = get_graph()
    return graph

def silhouette_bar(score_si, labels, title_sc = 'Silhouette plot for the various clusters'):
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
        ax.set_title(title_sc)

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

def sales_plot(x, y, kind):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()
    # ax.set_ylim(-1,1)
    # ax.set_xlim(min(x)-0.5,max(x)+0.5)
    plt.plot(x,y)
    if(kind == 'income'):
        ax.set_ylim(min(y)-5000000,max(y)+5000000)
        plt.title('Income every year')
        plt.ylabel('Money (Rp)')
    if(kind == 'order'):
        ax.set_ylim(min(y)-300,max(y)+300)
        plt.title('Order every year')
        plt.ylabel('Count order')
    plt.xlabel('Years')
    for i,j in zip(x,y):
        ax.annotate(str(j),xy=(i,j))
    
    graph = get_graph()
    return graph

def testing_sc_bar(x, data, title):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()
    fig.set_figwidth(12)

    x_base = x
    x1 = [x-0.2*2 for x in x_base]
    x2 = [x-0.2 for x in x_base]
    x3 = [x for x in x_base]
    x4 = [x+0.2 for x in x_base]

    y1 = [round(sc,3) for sc in data[0]]
    y2 = [round(sc,3) for sc in data[1]]
    y3 = [round(sc,3) for sc in data[2]]
    y4 = [round(sc,3) for sc in data[3]]

    width = 0.2

    rects1 = ax.bar(x1, y1, width, label='Bobot 1')
    rects2 = ax.bar(x2, y2, width, label='Bobot 2')
    rects3 = ax.bar(x3, y3, width, label='Bobot 3')
    rects4 = ax.bar(x4, y4, width, label='Tanpa Bobot')

    ax.set_ylabel('Scores')
    ax.set_xlabel('Jumlah k Cluster')
    ax.set_title(title)
    ax.set_xticks(x3)
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    ax.bar_label(rects4, padding=3)

    graph = get_graph()
    return graph

def persentage_horizontal_bar(x, y, x_label='X Label', y_label='Y Label', title='Horizontal Bar'):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()
    x = [ round((data/sum(x))*100,2) for data in x]
    if len(x)>12:
        x = x[len(x)-10:]       
        y = y[len(y)-10:]
    color_bar = ['orange' if c>len(x)-4 else 'blue' for c in range(len(x))]
    bars = plt.barh(y,x, color=color_bar)
    for bar in bars: 
        width = bar.get_width()
        label_y = bar.get_y() + bar.get_height() / 2
        plt.text(width, label_y, s=f'{width}%')
    
    ax.set_xlim(0, max(x)+5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    graph = get_graph()
    return graph

def hours_bar(x, y):
    plt.switch_backend('AGG')
    width = 0.5 # the width of the bars
    x = [ str(i) for i in range(len(x))]

    fig, ax = plt.subplots()
    # fig.set_figwidth(12)
    rects = ax.bar(x, y, width)

    ax.set_ylabel('Jumlah Pelanggan')
    ax.set_xlabel('Jam')
    ax.set_title('Jam Terakhir Transaksi Pelanggan')

    ax.bar_label(rects, padding=3)
    graph = get_graph()
    return graph

def pie_chart(data, labels, title="Pie Chart",title_legend="", legend_ket=[]):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', wedgeprops=dict(width=.7), startangle=90)
    ax.axis('equal')
    plt.title(title)
   
    
    plt.legend(legend_ket, loc='best', title=title_legend, fontsize=8)
    graph = get_graph()
    return graph
    
def grouped_two_bar(x, y1, y2, x_label = "X Label", y_label = "Y Label", y1_label = "Y1", y2_label = "Y2", title = "Bar Chart"):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots()

    x_base = np.arange(len(x))
    width = 0.35    
    rects1 = ax.bar(x_base - width/2, y1, width, label=y1_label)
    rects2 = ax.bar(x_base + width/2, y2, width, label=y2_label)

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    ax.set_xticks(x_base, x)
    ax.legend()

    graph = get_graph()
    return graph





