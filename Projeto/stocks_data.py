from stock_app import Stock

import numpy as np

class Stocks_data:

    def __init__(self):
        self.symbol_lst = []
        self.n_symbols = 0
        print(self.n_symbols)
        # Initialization of the array that stores our Stock objects
        self.stocks_array = []


    def remove_stock(self, symbol):
        idx = self.symbol_lst(symbol)                               # Get index of the symbol remove
        self.symbol_lst.remove(symbol)                              # Remove symbol from the list
        self.stocks_array.remove(symbol)                            # Remove the stock from the stock_array
        self.n_symbols -= 1                                         # Update the number of symbols
        Stock.n_stocks = self.n_symbols                             # Update the number of stocks on the Stock class
        for i in range(self.n_symbols):                             # Remove the other stocks correlations with the stock removed
            self.stocks_data[i].correlation.pop(idx)


    def add_stock(self, symbol):
        self.n_symbols += 1
        Stock.n_stocks = self.n_symbols
        try:
            stock = Stock(symbol)
            self.stocks_array.append(stock)
            self.symbol_lst.append(symbol)
            for i in range(self.n_symbols-1):    
                self.stocks_array[i].correlation.append(0)       
            return 0
        except ValueError as e:
            self.n_symbols -= 1
            Stock.n_stocks = self.n_symbols
            return str(e)
                  

    def init_metrics(self):
        for i in range(self.n_symbols):
            self.stocks_array[i].init_metrics()
        for i in range(self.n_symbols):
            for j in range(i, self.n_symbols):
                if i == j:
                    self.stocks_array[i].correlation[j] = 1
                else:
                    self.stocks_array[i].calc_correlation(j, self.stocks_array[j].deviations, self.stocks_array[j].std_dev)
                    self.stocks_array[j].correlation[i] = self.stocks_array[i].correlation[j]
