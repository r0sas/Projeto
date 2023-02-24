import numpy as np
import pandas as pd
import bs4
import requests
import math
import matplotlib.pyplot as plt

from collections import deque

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
def get_close(stock,time_dim):
    history_url = "https://finance.yahoo.com/quote/" + stock + "/history?p=" + stock #concatenação de strings para obter a webpage da respetiva stock
    doc = get_page(history_url)                     #obter dados da página    
    table_body = doc.find('tbody')                  #selecionar tabela de dados
    rows = table_body.find_all('tr')                #selecionar colunas
    close_data = deque(maxlen=time_dim)      #criação do queue onde iremos guardar os dados de close
    i = 0
    for row in rows:
        cols=row.find_all('td')                     #obtenção de colunas
        cols=[x.text.strip() for x in cols]
        try:                                        #Irá verificar se a coluna não tem informações acerca de stocks_split
            float(cols[-2])
        except:
            pass
        else:
            close_data.append(float(cols[-2]))         #guardar os dados do close, que estão na última coluna
            i += 1;
        if i == time_dim:
            break
    return close_data

#obter as datas de cada dia em que obtivemos o close (é comum para todas as stocks)
def get_timeline(stock, time_dim):
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
        if i == time_dim:
            break
    return timeline

#obter a rentabilidade
    #parametros de entrada:
        #dados de close e numero de dias
    #parametros de saida:
        #rentabilidade, retorno
def get_rentability(close_data, time_dim):
    log_close_data = np.log(np.array(close_data))
    rtbly = deque(maxlen=time_dim-1)                    #onde irei guardar a rentabilidade
    for i in range(1,time_dim):
        rtbly.append(log_close_data[i] - log_close_data[i-1])
    rtn = sum(rtbly) / (time_dim-1)                  #calculo do retorno
    return rtbly, rtn

#obter a variancia, coeficiente de variação e desvio_padrão
    #parametros de entrada:
        #dados de rentabilidade, retorno e numero de dias
    #parametros de saida:
        #variancia, coeficiente de variação e desvio_padrão
def get_var_cv(rtbly, rtn, time_dim):
    var = 0
    for x in rtbly:                                 #somatorio dos desvios ao quadrado
        var += (x - rtn)**2
    var = var/(time_dim-2)                   #divisão por numero de pontos -1, está -2 porque temos menos 1 valor do que o numero de dias
    cv = math.sqrt(var)/rtn
    std_dev = math.sqrt(var)
    return var, cv, std_dev

#calcular a correlação de stocks
    #parametros de entrada:
        #variancia, rentabilidade e retorno das duas stocks e numero de pontos dos dias
    #parametros de saida:
        #quoficiente de correlação
def correlation(std_dev_i, std_dev_j, rtbly_i, rtbly_j, rtn_i, rtn_j, time_dim):
    cov_ij = 0
    for k in range(time_dim-1):
        cov_ij += (rtbly_i[k] - rtn_i)*(rtbly_j[k] - rtn_j)
    cov_ij = cov_ij/(time_dim-2)
    corr = cov_ij / (std_dev_i*std_dev_j)
    if corr > 1:
        corr = 1
    return corr

#"VTI", "VNQ", "GLD", "BND"
tickers_lst = ["TSLA", "NIO", "RIVN", "LCID", "XPEV"]


time_dim = 60

stocks_data = {}

timeline = get_timeline("TSLA", time_dim)

for stock in tickers_lst:
    close = get_close(stock,time_dim)  ##obter os dados de close
    rtbly, rtn = get_rentability(close,time_dim) ##obter os dados de rentabilidade e retorno
    var, cv, std_dev = get_var_cv(rtbly, rtn, time_dim) #obter os dados de variância e covariância
    stocks_data[stock] = {"close" : close, "rentability" : rtbly, "return" : rtn, "variance" : var, "covariance" : cv, "standard deviation": std_dev}

#usar o index para dar skip a valores ja calculados previamente ij = ji
for stock_i in tickers_lst:
    corr_i = []
    for stock_j in tickers_lst:
        if stock_i == stock_j:
            corr_i.append(1)
        else:
            corr = correlation(stocks_data[stock_i]["standard deviation"], stocks_data[stock_j]["standard deviation"],
                   stocks_data[stock_i]["rentability"], stocks_data[stock_j]["rentability"],
                   stocks_data[stock_i]["return"], stocks_data[stock_j]["return"],
                   time_dim)
            corr_i.append(corr)
    stocks_data[stock_i]["correlations"] = corr_i;

n_tickers = len(tickers_lst)
#correlation matrix
corr_matrix = np.zeros((n_tickers, n_tickers))

#calculate distance matrix
d = np.zeros((n_tickers, n_tickers))
for i in range(n_tickers):
    correlations = stocks_data[tickers_lst[i]]["correlations"]
    corr_matrix[i,:] = correlations
    for j in range(i,n_tickers):
        dij = math.sqrt(2*(1-correlations[j]))
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
print("--------------------------------------------")

#calculate multidimensional scaling
ij = np.zeros((2,1))
min = 100000000
for i in range(d.shape[0]-1):
    xi = d[i]
    for j in range(i+1,d.shape[0]):
        xj = d[j]
        argmin = (np.linalg.norm(xi-xj) - d[i,j])**2
    if argmin < min:
        ij = [i, j]
print(ij[0],ij[1])
fig = plt.figure(2, (10,4))
ax = fig.add_subplot(121)

plt.scatter(corr_matrix[ij[0],:], corr_matrix[ij[1],:])
for i in range(n_tickers):
    plt.annotate(tickers_lst[i], (corr_matrix[ij[0],:][i], corr_matrix[ij[1],:][i]))
plt.title("Multidimensional scaling")

ax = fig.add_subplot(122)
legend = []
x = np.arange(0,time_dim,1)

for stock in tickers_lst:
    legend.append(stock)
    print(stock, "correlations: ")
    correlations = stocks_data[stock]["correlations"]
    for i in range(n_tickers):
        print("Stock ",tickers_lst[i],"\tCorrelation: ", correlations[i])
    print("Standard Deviation: ", math.sqrt(stocks_data[stock]["variance"]))
    plt.plot(x,np.log(stocks_data[stock]["close"]))
plt.xticks(x, timeline, rotation=45, fontsize='5', horizontalalignment='right')
plt.title("Close")
plt.legend(legend)
plt.show()

