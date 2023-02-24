import numpy as np
import pandas as pd
import bs4
import requests
import math
import matplotlib.pyplot as plt

from collections import deque
import time

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


#obter os dados de close de uma stock para quando a bolsa de valores está aberta
    #parametros de entrada:
        #ticker da stock
    #parametros de saida:
        #valor de close 
def get_close(stock_ticker):
    history_url = "https://finance.yahoo.com/quote/" + stock_ticker + "/history?p=" + stock_ticker #concatenação de strings para obter a webpage da respetiva stock
    doc = get_page(history_url)                     #obter dados da página
    text = doc.find_all("fin-streamer", class_="Fw(b) Fz(36px) Mb(-4px) D(ib)")
    return (float(text[0].text))


#obter os dados de close de uma stock para horário fora do 
    #parametros de entrada:
        #ticker da stock
    #parametros de saida:
        #valor de close 
def get_pa_close(stock_ticker):
    history_url = "https://finance.yahoo.com/quote/" + stock_ticker + "/history?p=" + stock_ticker #concatenação de strings para obter a webpage da respetiva stock
    doc = get_page(history_url)                     #obter dados da página
    text = doc.find_all("fin-streamer", class_="C($primaryColor) Fz(24px) Fw(b)")
    return (float(text[0].text))

def init_close(ticker_lst, time_dim):
    current_dim = 0
    for ticker in ticker_lst:
        close_data = deque(maxlen=time_dim)
        log_close_data = deque(maxlen=time_dim)
        rtbly = deque(maxlen=time_dim-1)
        corr = np.zeros((len(ticker_lst),1))
        stocks_data[ticker] = {"close": close_data, 
                               "log_close": log_close_data,
                               "rtbly": rtbly,
                               "rtn": 0,
                               "var": 0,
                               "std_dev": 0,
                               "coef_var": 0,
                               "corr": corr}

    while current_dim < time_dim:
        start_time = time.time()
        for ticker in ticker_lst:
            close_value = get_close(ticker)
            stocks_data[ticker]["close"].append(close_value)
            stocks_data[ticker]["log_close"].append(math.log(close_value))
        
        elapsed_time = time.time() - start_time
        if elapsed_time < 30:
            time.sleep(30 - elapsed_time)
        current_dim += 1
        print("------------------------------------------")
        for ticker in ticker_lst:
            print(stocks_data[ticker]["close"])
            print("******************************************")
        print("\n")
    time.sleep(30)


#initialize the return and rentability data
def init_rtbly(tickers_lst, time_dim):
    for ticker in tickers_lst:
        for i in range(1,time_dim):
            stocks_data[ticker]["rtbly"].append(stocks_data[ticker]["log_close"][i] - stocks_data[ticker]["log_close"][i-1])
        stocks_data[ticker]["rtn"] = sum(stocks_data[ticker]["rtbly"]) / (time_dim - 1)
        #print("------------------ Init Rentability ------------------")
        #print(stocks_data[ticker]["rtn"])

#initialize risk data (variation, coeficient of variation, standard deviation)
def calc_risk(ticker_lst, time_dim):
    for ticker in ticker_lst:
        var = 0
        rtn = stocks_data[ticker]["rtn"]
        #print("Contas Risk")
        #print("---------------Desvios-------------")
        for value in stocks_data[ticker]["rtbly"]:
            var += (value-rtn)**2
            #print((value-rtn)**2)
        if rtn == 0: ################check this
            rtn = 1
        if var == 0:
            var = 1
        var = var/(time_dim-2)
        stocks_data[ticker]["var"] = var
        stocks_data[ticker]["coef_var"] = math.sqrt(var)/rtn
        stocks_data[ticker]["std_dev"] = math.sqrt(var)

#calculation of correlation
#iteration of stocks 2 cycles are needed for comparison
    #iteration of the values of stocks and calculation of covariance for each point in time
    

def calc_correlation(ticker_lst, time_dim):
    for i in range(len(ticker_lst)):
        for j in range(len(ticker_lst)):
            if i == j:
                stocks_data[ticker_lst[i]]["corr"][j] = 1
            else:
                cov_ij = 0
                for k in range(time_dim-1):
                    cov_ij += ((stocks_data[ticker_lst[i]]["rtbly"][k] - stocks_data[ticker_lst[i]]["rtn"]) *
                               (stocks_data[ticker_lst[j]]["rtbly"][k] - stocks_data[ticker_lst[j]]["rtn"]))
                    #print("cov_ij ", k, " :", ((stocks_data[ticker_lst[i]]["rtbly"][k] - stocks_data[ticker_lst[i]]["rtn"]) *
                               #(stocks_data[ticker_lst[j]]["rtbly"][k] - stocks_data[ticker_lst[j]]["rtn"])))
                cov_ij = cov_ij/(time_dim-2)
                #print("Covariância ", ticker_lst[i]," :", cov_ij)
                corr = cov_ij/(stocks_data[ticker_lst[i]]["std_dev"]*stocks_data[ticker_lst[j]]["std_dev"])
                if corr > 1:
                    stocks_data[ticker_lst[i]]["corr"][j] = 1
                else:
                    stocks_data[ticker_lst[i]]["corr"][j] = corr

#to update rentability efficiently we get the "old value", it's the one that will be removed from the deque of rentability
#we calculate the new value and add it the rentability
#to be computationally more efficient, since the return is a sum of all the values of rentability divided by (n-1) we can substract the old value and add the new one,
#instead of computing all elements
def update_rtbly(ticker, time_dim):
    old_value = stocks_data[ticker]["rtbly"][0]
    new_value = stocks_data[ticker]["log_close"][time_dim-1] - stocks_data[ticker]["log_close"][time_dim-2] ###indices ao contrário
    stocks_data[ticker]["rtbly"].append(new_value)
    stocks_data[ticker]["rtn"] = ( stocks_data[ticker]["rtn"] + (new_value - old_value) / (time_dim - 1) )


#we get the new value for the close and calculate new metrics taking into account this new value
#and exclude the oldest value
    #calculate rentability and return
    #calculate variation, coeficient of variation and standard deviation
    #calculate the correlation of stocks
def update_data(ticker_lst, time_dim):
    for ticker in ticker_lst:
        print("---------------------", ticker, "--------------------")
        close_value = get_close(ticker)
        print("Close Value :", close_value)
        stocks_data[ticker]["close"].append(close_value)
        stocks_data[ticker]["log_close"].append(math.log(close_value))
    for ticker in ticker_lst:
        #print("---------------------", ticker, "---------------------")
        #print("__________________Log Close _______________________")
        #print(stocks_data[ticker]["log_close"])
        update_rtbly(ticker, time_dim)
        #print("__________________ Rentabilidade _____________________")
        #print(stocks_data[ticker]["rtbly"])
        #print("__________________ Retorno _____________________")
        #print(stocks_data[ticker]["rtn"])
        calc_risk(ticker_lst, time_dim)
        #print("___________________Desvio Padrão_____________________")
        #print(stocks_data[ticker]["std_dev"])
    for ticker in ticker_lst:
        print("---------------------", ticker, "---------------------")
        calc_correlation(ticker_lst, time_dim)
        print("___________________Correlação_____________________")
        print(stocks_data[ticker]["corr"])
        print("########################")


stocks_data = {}
def main():
    ticker_lst = ["TSLA", "AMZN"]
    time_dim = 5

    current_time = time.time()
    # Round up to the nearest minute
    next_minute = int(current_time / 60) * 60 + 60
    # Calculate the number of seconds until the next minute
    sleep_time = next_minute - current_time
    # Sleep until the next minute
    time.sleep(sleep_time)

    init_close(ticker_lst, time_dim)
    init_rtbly(ticker_lst, time_dim)
    calc_risk(ticker_lst, time_dim)
    calc_correlation(ticker_lst, time_dim)
    #for ticker in ticker_lst:
        #print("__________________Log Close _______________________")
        #print(stocks_data[ticker]["log_close"])
        #print("__________________ Rentabilidade _____________________")
        #print(stocks_data[ticker]["rtbly"])
        #print("___________________Desvio Padrão_____________________")
        #print(stocks_data[ticker]["std_dev"])
        #print("_____________Correlações________________")
        #print(stocks_data[ticker]["corr"])
        #print("########################")
    while True:
        start_time = time.time()
        update_data(ticker_lst, time_dim)
        elapsed_time = time.time() - start_time
        if elapsed_time < 30:
            time.sleep(30 - elapsed_time)


if __name__ == "__main__":
    main()
