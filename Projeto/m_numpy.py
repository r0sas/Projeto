import numpy as np
import pandas as pd
import bs4
import requests
import math
import matplotlib.pyplot as plt
#from collections import deque

#obter o codigo fonte da webpage
def get_page(url):
    """Download a webpage and return a beautiful soup doc"""
    response = requests.get(url, headers={'User-Agent': 'Custom'}) # to try and pass as a person accessing the website
    if not response.ok:
        print('Status code:', response.status_code)
        raise Exception('Failed to load page {}'.format(url))
    page_content = response.text
    doc = bs4.BeautifulSoup(page_content, 'html.parser')
    return doc

#obter os dados de close de uma stock
    #parametros de entrada:
        #ticker da stock, numero de dias
    #parametros de saida:
        #dados de close 
def get_close(stock,num_hist_points):
    history_url = "https://finance.yahoo.com/quote/" + stock + "/history?p=" + stock #concatenação de strings para obter a webpage da respetiva stock
    doc = get_page(history_url)                     #obter dados da página    
    table_body = doc.find('tbody')                  #selecionar tabela de dados
    rows = table_body.find_all('tr')                #selecionar colunas
    close_data = np.zeros((num_hist_points,1))      #criação do array onde iremos guardar os dados de close
    i = 0
    for row in rows:
        cols=row.find_all('td')                     #obtenção de colunas
        cols=[x.text.strip() for x in cols]
        try:                                        #Irá verificar se a coluna não tem informações acerca de stocks_split
            float(cols[-2])
        except:
            pass
        else:
            close_data[i] = float(cols[-2])         #guardar os dados do close, que estão na última coluna
            i += 1;
        if i == num_hist_points:
            break
    return close_data

#obter a rentabilidade
    #parametros de entrada:
        #dados de close e numero de dias
    #parametros de saida:
        #rentabilidade, retorno
def get_rentability(close_data, num_hist_points):
    log_close_data = np.log(close_data)
    rtbly = np.zeros((num_hist_points-1,1)   )      #onde irei guardar a rentabilidade
    for i in range(1,num_hist_points):
        rtbly[i-1] = log_close_data[i] - log_close_data[i-1]
    rtn = np.sum(rtbly) / (num_hist_points-1) #calculo do retorno
    return rtbly, rtn

#obter a variancia e covariancia
    #parametros de entrada:
        #dados de rentabilidade, retorn e numero de dias
    #parametros de saida:
        #variancia, coeficiente de variação
def get_var_cv(rtbly, rtn, num_hist_points):
    var = 0
    for x in rtbly:                                 #somatorio dos desvios ao quadrado
        var += (x - rtn)**2
    var = var/(num_hist_points-2)                   #divisão por numero de pontos -1, está -2 porque temos menos 1 valor do que o numero de dias
    cv = math.sqrt(var)/rtn
    return var, cv

#calcular a correlação de stocks
    #parametros de entrada:
        #variancia, rentabilidade e retorno das duas stocks e numero de pontos dos dias
    #parametros de saida:
        #quoficiente de correlação
def correlation(var_i, var_j, rtbly_i, rtbly_j, rtn_i, rtn_j, num_hist_points):
    cov_ij = 0
    for k in range(num_hist_points-1):
        cov_ij = cov_ij + (rtbly_i[k] - rtn_i)*(rtbly_j[k] - rtn_j)
    cov_ij = cov_ij/(num_hist_points-2)
    corr = cov_ij / (math.sqrt(var_i)*(math.sqrt(var_j)))
    if corr > 1:
        corr = 1
    return corr

#obter as datas de cada dia em que obtivemos o close (é comum para todas as stocks)
def get_timeline(stock, num_hist_points):
    history_url = "https://finance.yahoo.com/quote/" + stock + "/history?p=" + stock    #concatenação de strings para obter a webpage da respetiva stock
    doc = get_page(history_url)                     #obter dados da página    
    table_body = doc.find('tbody')                  #selecionar tabela de dados
    rows = table_body.find_all('tr')                #selecionar colunas
    timeline = []                                   #criação do array onde iremos guardar os dados
    i = 0
    for row in rows:
        cols=row.find_all('td')                     #obtenção de colunas
        cols=[x.text.strip() for x in cols]
        try:                                        #Irá verificar se a coluna não tem informações acerca de stocks_split
            float(cols[-2])
        except:
            pass
        timeline.append(cols[0])      
        i += 1;
        if i == num_hist_points:
            break
    return timeline

#"VTI", "VNQ", "GLD", "BND"
stocks_lst = ["TSLA", "NIO", "RIVN", "LCID", "XPEV"]


num_hist_points = 60

stocks_data = {}

timeline = get_timeline("TSLA", num_hist_points)

for stock in stocks_lst:
    close = get_close(stock,num_hist_points)
    rtbly, rtn = get_rentability(close,num_hist_points)
    var, cv = get_var_cv(rtbly, rtn, num_hist_points)
    stocks_data[stock] = {"close" : close, "rentability" : rtbly, "return" : rtn, "variance" : var, "covariance" : cv}



#usar o index para dar skip a valores ja calculados previamente ij = ji
for stock_i in stocks_lst:
    corr_i = []
    for stock_j in stocks_lst:
        if stock_i == stock_j:
            corr_i.append([stock_j,1])
        else:
            corr = correlation(stocks_data[stock_i]["variance"], stocks_data[stock_j]["variance"],
                   stocks_data[stock_i]["rentability"], stocks_data[stock_j]["rentability"],
                   stocks_data[stock_i]["return"], stocks_data[stock_j]["return"],
                   num_hist_points)
            corr_i.append([stock_j,corr])
    stocks_data[stock_i]["correlations"] = corr_i;


n_stocks = len(stocks_lst)
#correlation matrix
corr_matrix = np.zeros((n_stocks, n_stocks))

#calculate distance matrix
d = np.zeros((n_stocks, n_stocks))
for i in range(n_stocks):
    correlations = stocks_data[stocks_lst[i]]["correlations"]
    #stock_corr = np.ones((1,5))
    #for j in range(n_stocks):
    #    stock_corr[j] = correlations[j][1]
    #corr_matrix[i,:] = stock_corr
    for j in range(i,n_stocks):
        dij = math.sqrt(2*(1-correlations[j][1]))
        d[i,j] = dij
        d[j,i] = dij

for row in d:
    print(row)


eigenvalues, eigenvectors = np.linalg.eig(corr_matrix)
idx = eigenvalues.argsort()[::-1]   
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:,idx]
k = 2
top_k_eigenvectors = eigenvectors[:,:k]
pos = top_k_eigenvectors * np.sqrt(eigenvalues[:k])
print("--------------------------------------------")
for x in pos:
    print(x)


#calculate multidimensional scaling
ij = np.zeros((2,1))
for i in range(d.shape[0]-1):
    xi = d[i]
    min = 100000000
    for j in range(i+1,d.shape[0]):
        xj = d[j]
        argmin = (np.linalg.norm(xi-xj) - d[i,j])**2
    if argmin < min:
        ij = [i, j]
print(ij[0],ij[1])
fig = plt.figure(2, (10,4))
ax = fig.add_subplot(121)

plt.scatter(d[ij[0]], d[ij[1]])
for i in range(n_stocks):
    plt.annotate(stocks_lst[i], (d[ij[0]][i]+.01, d[ij[1]][i]))
plt.title("Multidimensional scaling")

ax = fig.add_subplot(122)
legend = []
x = np.arange(0,num_hist_points,1)

for stock in stocks_lst:
    legend.append(stock)
    print(stock, "correlations: ")
    correlations = stocks_data[stock]["correlations"]
    for corr in correlations:
        print("Stock ",corr[0],"\tCorrelation: ", corr[1])
    print("Standard Deviation: ", math.sqrt(stocks_data[stock]["variance"]))
    plt.plot(x,np.log(stocks_data[stock]["close"]))
plt.xticks(x, timeline, rotation=45, fontsize='5', horizontalalignment='right')
plt.title("Close")
plt.legend(legend)
plt.show()
