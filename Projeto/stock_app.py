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
        self.prev_market_state = None

        result = self.init_close()
        if result == 1:
            raise ValueError("Didn't find the Stock: " + symbol + "\n")
        elif result == 2:
            raise ValueError("Due the high frequency of webscraping couldn't webscrape the Stock: " + symbol + ", you should try again after some time\n")
        elif result == 3:
            raise ValueError("Didn't gather enough data for the Stock Symbol: " + symbol + "\n")
        else:
            self.close_data.reverse()
            self.log_close_data.reverse()

        if self.check_market_status() == 1:
            self.prev_market_state = "Market Open"
        else: 
            self.prev_market_state = "Market Close"

    # Get webpage code
    def webscrape_page(self,url):
        """Download a webpage and return a beautiful soup doc"""
        response = requests.get(url, headers={'User-Agent': 'Custom'}) # to try and pass as a person accessing the website
        if response.history:
            return 1
        if not response.ok:
            print('Status code:', response.status_code)
            return 2
        page_content = response.text
        doc = bs4.BeautifulSoup(page_content, 'html.parser')
        return doc

    # Get the past n_ticks close values 
    def init_close(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.webscrape_page(history_url)                     #obter dados da página
        if doc == 1 or doc == 2:
            return doc
        table_body = doc.find('tbody')                  #selecionar tabela de dados
        rows = table_body.find_all('tr')                #selecionar colunas
        i = 0
        for row in rows:
            cols=row.find_all('td')                     #obtenção de colunas
            cols=[x.text.strip() for x in cols]
            value = cols[-2]
            if "," in value:                            # Removes commas from numbers
                value = value.replace(",", "")
            try:                                        #Irá verificar se a coluna não tem informações acerca de stocks_split
                float(value)
            except:
                pass
            else:
                self.close_data.append(float(value))         #guardar os dados do close, que estão na última coluna
                self.log_close_data.append(math.log(float(value)))
                i += 1;
            if i == self.n_ticks:
                break
        if i != self.n_ticks:
            return 3
        return 0

    # Calculates the rentability 
    def calc_rentability(self):              
        for i in range(1, self.n_ticks):
            self.rentability.append(self.log_close_data[i] - self.log_close_data[i-1])

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
        if self.rtn == 0:                                               # Case of stock price is static
            self.variance = 0
            self.coef_var = 0
        else:
            self.coef_var = math.sqrt(self.variance) / self.rtn
            self.std_dev = math.sqrt(self.variance)

        # Calculate the correlation of this stock and another
    def calc_correlation(self, j, deviations_j, std_dev_j):
        if (self.rtn == 0) & (self.coef_var == 0):                      # Caso of stock price being static
            self.correlation[j] = corr_ij
            return 1
        else:
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
    def webscrape_close(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.webscrape_page(history_url)                     #obter dados da página
        text = doc.find_all("fin-streamer", class_="Fw(b) Fz(36px) Mb(-4px) D(ib)")
        return (float(text[0].text))

    # Get the current close data
    # Save the new value in the deque
    # Save the log of the new value for the close on another deque
    def add_close(self):
        close_value = self.webscrape_close()
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

    def check_market_status(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.webscrape_page(history_url)                     # Webscrapes the page
        if doc == 2:
            raise ValueError("Didn't find the Stock : " + self.symbol + "\n")
        if doc == 3:
            raise ValueError("Due the high frequency of webscraping couldn't webscrape the Stock Symbol: " + self.symbol + ", you should try again after some time\n")
        text = doc.find_all("div", {"id": "quote-market-notice"})
        print(text)
        market_state = ( str(text).replace(".</span></div>]","") ).split(". ")
        print(market_state)
        if len(market_state) == 2:  #analisar melhor as condições no sentido a  retirar o if possiblidade de iniciar com "Market open"
            self.prev_market_state == "Market Open"
            return 1                                                                         # Está aberto
        elif self.prev_market_state == "Market Open":                                        # This is the case where it manages to successfully webscrape "Market Open"
        #if (self.prev_market_state == "Market Open" & market_state != self.market_state):
            self.prev_market_state = "Market Close"
            return 0                                                    #passa de aberto para fechado
        else:
            return 2