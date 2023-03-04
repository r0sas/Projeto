import bs4
import requests
import math
import matplotlib.pyplot as plt
import numpy as np

from collections import deque

class Stock:
    # Class-level variables
    n_ticks = 60                                         # class-level variable with the number of ticks
    n_stocks = 0                                        # class-level variable with the number of stocks

    # Inicialization of the object
    def __init__(self, symbol: str):
        self.symbol: str = symbol                               # symbol symbol
        self.close_data = deque(maxlen = Stock.n_ticks)         # deque with close values
        self.log_close_data = deque(maxlen = Stock.n_ticks)     # deque with logaritmic close values
        self.rentability = deque(maxlen = (Stock.n_ticks - 1))  # deque with rentability values
        self.deviations = deque(maxlen = (Stock.n_ticks - 1))   # deque with deviation values
        self.correlation = [0] * Stock.n_stocks                 # list with correlation values
        self.rtn = None                                 # variable with return value
        self.variance = None                            # variable with variance value
        self.std_dev = None                             # variable with standard deviation value
        self.coef_var = None                            # variable with coeficient of variation value
        result = self.init_close()
        if result == 1:
            raise ValueError("Stock symbol not found")


    # Get webpage code
    def get_page(self,url):
        """Download a webpage and return a beautiful soup doc"""
        response = requests.get(url, headers={'User-Agent': 'Custom'}) # to try and pass as a person accessing the website
        if response.history:
            return 1
        if not response.ok:
            print('Status code:', response.status_code)
            raise Exception('Failed to load page {}'.format(url))
        page_content = response.text
        doc = bs4.BeautifulSoup(page_content, 'html.parser')
        return doc

    # Get the past n_ticks close values 
    def init_close(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.get_page(history_url)                     #obter dados da página
        if doc == 1:
            return 1
        table_body = doc.find('tbody')                  #selecionar tabela de dados
        rows = table_body.find_all('tr')                #selecionar colunas
        i = 0
        for row in rows:
            cols=row.find_all('td')                     #obtenção de colunas
            cols=[x.text.strip() for x in cols]
            try:                                        #Irá verificar se a coluna não tem informações acerca de stocks_split
                float(cols[-2])
            except:
                pass
            else:
                self.close_data.append(float(cols[-2]))         #guardar os dados do close, que estão na última coluna
                self.log_close_data.append(math.log(float(cols[-2])))
                i += 1;
            if i == self.n_ticks:
                break
        return 0

    def calc_rentability(self):
        for i in range(1, self.n_ticks):
            self.rentability.append(self.log_close_data[i]- self.log_close_data[i-1])


    # Calculate the return value
    def calc_return(self):
        self.rtn = sum(self.rentability) / (Stock.n_ticks-1)

    def calc_deviations(self):
        #possible use of numpy
        self.deviations = deque([value - self.rtn for value in self.rentability])

    # Calculate some risk metrics
        # calculate variance
        # calculate standard deviation
        # calculate coeficient of variation
    def calc_risk(self):
        self.variance = sum(value**2 for value in self.deviations) / (Stock.n_ticks-2)
        #check this and put this before the cycle "for" since if rtn = 0 it implies var = 0
        if self.rtn == 0:
            self.rtn = 1
            self.variance = 1
        self.coef_var = math.sqrt(self.variance) / self.rtn
        self.std_dev = math.sqrt(self.variance)

        # Calculate the correlation of this stock and another
    def calc_correlation(self, j, deviations_j, std_dev_j):
        cov_ij = sum(value_i * value_j for value_i, value_j 
                     in zip(self.deviations, deviations_j)) / (Stock.n_ticks-2)
        corr_ij = cov_ij / (self.std_dev*std_dev_j)
        self.correlation[j] = corr_ij


    # Updates the value of rentability and return
    # To update the value of return we subtract the element that's going to "leave"
    #   the deque rentability and sum the added value of rentability
    def update_rentability(self):
        old_value = self.rentability[0]
        new_value = self.log_close_data[Stock.n_ticks-1] - self.log_close_data[Stock.n_ticks-2]
        self.rentability.append(new_value)
        self.rtn = self.rtn + (new_value-old_value) / (Stock.n_ticks - 1)
    
    # Get the current close data
    def get_close(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.get_page(history_url)                     #obter dados da página
        text = doc.find_all("fin-streamer", class_="Fw(b) Fz(36px) Mb(-4px) D(ib)")
        return (float(text[0].text))

    # Get the current close data
    # Save the new value in the deque
    # Save the log of the new value for the close on another deque
    def add_close(self):
        close_value = self.get_close()
        self.close_data.append(close_value)
        self.log_close_data.append(math.log(close_value))

    def init_metrics(self):
        self.calc_rentability()
        self.calc_return()
        self.calc_deviations()
        self.calc_risk()
        

    # Updates the values:
        # close, log_close
        # rentability, rtn
        # deviations
        # variance, standard_deviation, coeficient of variation
    def update_data(self):
        self.add_close()
        self.update_rentability()
        self.calc_deviations()
        self.calc_risk()


