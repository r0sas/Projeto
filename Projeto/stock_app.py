from ast import Try
import bs4
import requests
import math
import matplotlib.pyplot as plt
import numpy as np
import itertools
from collections import deque

class Stock:
    # Class-level variables
    n_ticks = 30                                         # class-level variable with the number of ticks
    n_stocks = 0                                        # class-level variable with the number of stocks
    n_windows = 30

    # Inicialization of the object
    def __init__(self, symbol: str):
        self.symbol: str = symbol                               # symbol symbol
        self.close_data = deque(maxlen = Stock.n_ticks + Stock.n_windows -1)         # deque with close values
        self.log_close_data = deque(maxlen = Stock.n_ticks + Stock.n_windows -1)     # deque with logaritmic close values
        self.rentability = deque(maxlen = (Stock.n_ticks + Stock.n_windows - 2))  # deque with rentability values
        self.curr_rentability = deque(maxlen = (Stock.n_ticks-1))
        self.deviations = deque(maxlen = (Stock.n_ticks - 1))   # deque with deviation values
        self.correlation = None                 # list with correlation values
        self.correlations_history = [deque(maxlen=Stock.n_windows) for i in range(Stock.n_stocks)] # list with all correlations values for each stock
        self.rtn = deque(maxlen = Stock.n_windows)              # deque with return value
        self.variance = deque(maxlen = Stock.n_windows)         # deque with variance value
        self.std_dev = deque(maxlen = Stock.n_windows)          # deque with standard deviation value
        self.prev_market_state = None

        if self.check_market_status() == 1:
            self.prev_market_state = "Market Open"
        else: 
            self.prev_market_state = "Market Close"

        result = self.init_close()
        if result == 1:
            raise ValueError("Didn't find the Stock: " + symbol + "\n")
        elif result == 2:
            raise ValueError("Due the high frequency of webscraping couldn't fetch data for: " + symbol + ", you should try again after some time\n")
        elif result == 3:
            raise ValueError("Didn't gather enough data for the Stock Symbol: " + symbol + "\n")
        elif result == 4:
            raise ValueError("Max retries exceeded for " + symbol + "\n")
        else:
            self.close_data.reverse()
            self.log_close_data.reverse()

        self.init_metrics()

    # Get webpage code
    def webscrape_page(self,url):
        """Download a webpage and return a beautiful soup doc"""
        try: 
            response = requests.get(url, headers={'User-Agent': 'Custom'}) # to try and pass as a person accessing the website
            if response.history:
                return 1
            if not response.ok:
                print('Status code:', response.status_code)
                return 2
            page_content = response.text
            doc = bs4.BeautifulSoup(page_content, 'html.parser')
            return doc
        except:
            return 4

    # Get the past n_ticks close values 
    def init_close(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.webscrape_page(history_url)                     #obter dados da página
        if doc == 1 or doc == 2 or doc == 4:
            return doc
        table_body = doc.find('tbody')                  #selecionar tabela de dados
        rows = table_body.find_all('tr')                #selecionar colunas
        i = 0
        if self.prev_market_state == "Market Open":
            rows.pop(0)
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
            if i == (Stock.n_ticks + Stock.n_windows-1):
                break
        if i != (Stock.n_ticks + Stock.n_windows-1):
            return 3
        return 0

    # Calculates the rentability 
    def calc_rentability(self):              
        for i in range(1, (Stock.n_ticks + Stock.n_windows-1)):
            self.rentability.append(self.log_close_data[i] - self.log_close_data[i-1])

    # Calculate the return value
    def init_return(self):
        self.rtn.append( sum(self.curr_rentability) / (Stock.n_ticks - 1) )

    def calc_deviations(self,index):
        #possible use of numpy
        self.deviations = deque([value - self.rtn[index] for value in self.curr_rentability]) #dar update à rentabilidade

    # Calculate some risk metrics
        # calculate variance
        # calculate standard deviation
    def calc_risk(self, index):
        if self.rtn[index] == 0:                                               # Case of stock price is static
            self.variance.append(0)
            self.std_dev.append(0)
        else:
            self.variance.append(sum(value**2 for value in self.deviations) / (Stock.n_ticks-2))
            self.std_dev.append(math.sqrt(self.variance[index]))

    def init_metrics(self):
        self.calc_rentability()
        ([self.curr_rentability.append(self.rentability[i]) for i in range(self.n_ticks-1) ])
        self.init_return()
        self.calc_deviations(0)
        self.calc_risk(0)

    def update_metrics(self, index):
        self.update_rentability(index)
        self.calc_deviations(index)
        self.calc_risk(index)

        # Calculate the correlation of this stock and another
    def calc_correlation(self, j, deviations_j, std_dev_j, index):
        if self.std_dev[index] == 0:                                             # Case of stock price being static
            self.correlations_history[j].append(0)
            return 1, -1
        elif std_dev_j == 0:
            self.correlations_history[j].append(0)
            return 1, j
        else:
            cov_ij = sum(value_i * value_j for value_i, value_j 
                         in zip(self.deviations, deviations_j)) / (Stock.n_ticks-2)
            corr_ij = cov_ij / (self.std_dev[index]*std_dev_j)
            self.correlations_history[j].append(corr_ij)
            return 0, 0

    # Updates the value of rentability and return
    # To update the value of return we subtract the element that's going to "leave"
    #   the deque rentability and sum the added value of rentability
    def update_rentability(self, index):
        old_value = self.curr_rentability[0]
        new_value = self.rentability[Stock.n_ticks+index-2]
        self.curr_rentability.append(new_value)
        self.rtn.append( self.rtn[index-1] + ((new_value-old_value) / (Stock.n_ticks - 1)))
    
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

    # Updates the values:
        # close, log_close
        # rentability, rtn
        # deviations
        # variance, standard_deviation, coeficient of variation
    def update_metrics_realtime(self):
        self.add_close()
        self.update_rentability(Stock.n_windows-1)
        self.calc_deviations(Stock.n_windows-1)
        self.calc_risk(Stock.n_windows-1)

    def check_market_status(self):
        history_url = "https://finance.yahoo.com/quote/" + self.symbol + "/history?p=" + self.symbol #concatenação de strings para obter a webpage da respetiva stock
        doc = self.webscrape_page(history_url)                     # Webscrapes the page
        if doc == 1:
            raise ValueError("Didn't find the Stock: " + self.symbol + "\n")
        elif doc == 2:
            raise ValueError("Didn't find the Stock : " + self.symbol + "\n")
        elif doc == 4:
            raise ValueError("Due the high frequency of webscraping couldn't fetch data for: " + self.symbol + ", you should try again after some time\n")
        else:
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

    def get_deviations(self):
        return self.deviations

    def set_index(self, index):
        ([self.curr_rentability.append(self.rentability[i]) for i in range(index, self.n_ticks + index - 1) ])
        self.calc_deviations(index)
        
    def add_corr_space(self):
        self.correlations_history.append(deque(maxlen=Stock.n_windows))

    def set_last_correlation(self):
        self.correlation = [corr[Stock.n_windows-1] for corr in self.correlations_history]