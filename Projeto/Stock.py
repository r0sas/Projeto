class Stock(object):
    # class-level variables
    n_ticks = 0                                         # class-level variable with the number of ticks
    n_stocks = 0                                        # class-level variable with the number of stocks

    #Inicialization of the object
    def __init__(self, ticker: str):
        self.ticker: str = ticker                       # ticker symbol
        self.close_data = deque(maxlen = n_ticks)       # deque with close values
        self.log_close_data = deque(maxlen = n_ticks)   # deque with logaritmic close values
        self.rentability = deque(maxlen = n_ticks - 1)  # deque with rentability values
        self.deviations = deque(maxlen = n_ticks - 1)   # deque with deviation values
        self.correlation = np.zeros((n_stocks,1))       # deque with correlation values
        self.rtn = None                                 # variable with return value
        self.variance = None                            # variable with variance value
        self.std_dev = None                             # variable with standard deviation value
        self.coef_var = None                            # variable with coeficient of variation value

    # get webpage code
    def get_page(self,url):
        """Download a webpage and return a beautiful soup doc"""
        response = requests.get(url, headers={'User-Agent': 'Custom'}) # to try and pass as a person accessing the website
        if not response.ok:
            print('Status code:', response.status_code)
            raise Exception('Failed to load page {}'.format(url))
        page_content = response.text
        doc = bs4.BeautifulSoup(page_content, 'html.parser')
        return doc

    # get the current close data
    def get_close(self):
        history_url = "https://finance.yahoo.com/quote/" + self.ticker + "/history?p=" + self.ticker #concatenação de strings para obter a webpage da respetiva stock
        doc = self.get_page(history_url)                     #obter dados da página
        text = doc.find_all("fin-streamer", class_="Fw(b) Fz(36px) Mb(-4px) D(ib)")
        return (float(text[0].text))

    # get the current close data
    # save the new value in the deque
    # save the log of the new value for the close on another deque
    def add_close(self):
        close_value = self.get_close()
        self.close_data.append(close_value)
        self.log_close_data.append(math.log(close_value))

    # calculate rentability between 2 ticks
    def calc_rentability(self, tick=self.n_ticks):
        self.rentability.append(self.log_close_data[i] - self.log_close_data[i-1])

    # calculate the return value
    def calc_return(self):
        self.rtn = sum(self.rentability) / (n_ticks-1)

    def calc_deviations(self):
        self.deviations = self.rentability([value - self.rtn for value in self.rentability])

    # calculate some risk metrics
        # calculate variance
        # calculate standard deviation
        # calculate coeficient of variation
    def calc_risk(self):
        #check this and put this before the cycle "for" since if rtn = 0 it implies var = 0
        if self.rtn == 0:
            self.rtn = 1
            self.var = 1
        self.var = sum(value**2 for value in self.calc_deviations) / (n_ticks-2)
        self.var = self.var/(n_ticks-2)
        self.coef_var = math.sqrt(self.var)/self.rtn
        self.std_dev = math.sqrt(var)

    def calc_correlation(self, j, deviations_j, std_dev_j):
        cov_ij = sum(value_i * value_j for value_i, value_j 
                     in zip(self.deviations, deviations_j)) / (n_ticks-2)
        corr_ij = cov_ij / (self.std_dev*std_dev_j)

    # updates the value of rentability and return
    # to update the value of return we subtract the element that's going to "leave"
    #   the deque rentability and sum the added value of rentability
    def update_rentability(self):
        old_value = self.rentability[0]
        new_value = self.log_close_data[n_ticks-1] - self.log_close_data[n_ticks-2]
        self.rentability.append(new_value)
        self.rtn = self.rtn + (new_value-old_value) / (n_ticks - 1)
    
    # updates the values:
        # close, log_close
        # rentability, rtn
        # deviations
        # variance, standard_deviation, coeficient of variation
    def update_data(self):
        self.add_close()
        self.update_rentability()
        self.calc_deviations
        self.calc_risk()


