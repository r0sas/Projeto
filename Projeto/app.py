from stocks_data import Stocks_data
from stock_app import Stock

import threading as th
import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk


import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"



class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.checkbox_list = []
        self.info_btn_lst = []
        self.remove_btn_lst = []
        self.items_lst =[]

        for i, item in enumerate(item_list):
            self.add_item(item)

    def add_items(self, items):
        for item in items:
            if item not in self.items_lst:
                self.create_list_item(item)
                self.items_lst.append(item)
                print("Added: ", item)

    def create_list_item(self, item):
        checkbox = ctk.CTkCheckBox(self, text=item, width=150)
        info_btn = ctk.CTkButton(master=self, text="Info", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), width=80)
        remove_btn = ctk.CTkButton(master=self, text="-", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), width=40, command=lambda: self.remove_item(item))
        if self.command is not None:
            checkbox.configure(command=self.command)
        self.checkbox_list.append(checkbox)
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 10))
        info_btn.grid(row=len(self.checkbox_list), column=1, padx=(0,10), pady=(0, 10))
        remove_btn.grid(row=len(self.checkbox_list), column=2, pady=(0, 10), sticky="E")
        self.info_btn_lst.append(info_btn)
        self.remove_btn_lst.append(remove_btn)

    def update_items(self):
        for item in self.items_lst:
            print("Atualizei: ", item)
            self.create_list_item(item)

    # remover botões
    def remove_item(self, item):
        checked_items = self.get_checked_items()
        if item in checked_items:
            checked_items.remove(item)

        for i in range(len(self.items_lst)):
            if item == self.checkbox_list[0].cget("text"): #porque estou a fazer pop do elemento mais a direita
                print(self.items_lst)
                print(i, "Removi :", item)
                self.items_lst.pop(i)
            self.checkbox_list[0].destroy()
            self.info_btn_lst[0].destroy()
            self.remove_btn_lst[0].destroy()
            self.info_btn_lst.pop(0)
            self.remove_btn_lst.pop(0)
            self.checkbox_list.pop(0)    
            
        self.update_items()
        for checkbox in self.checkbox_list:
            if checkbox.cget("text") in checked_items:
                checkbox.select()
        app.plot_price(checked_items)
        return

    # return de lista com items com check
    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.n_ticks = 60
        Stock.n_sticks = self.n_ticks
        self.init_thread = False
        self.stocks_data = Stocks_data()
        self.symbols_lst = []

        # Configure window
        self.title("Financial Markets")
        self.geometry(f"{1100}x{580}")

        # Configure grid
            # weight = 0 fixo
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1), weight=0)

        # Side bar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Symbols entry
        self.entry_stocks = ctk.CTkEntry(self, placeholder_text = "Stocks (ex: TSLA, AMZN, META)", width=230)
        self.entry_stocks.grid(row=0, column=1, columnspan=2, padx=(10, 0), pady=(10, 10), sticky="nsew")
            
        # Symbols entry button
        self.add_symbols_btn = ctk.CTkButton(master=self, text="Add", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                command=self.add_stocks, width=50)
        self.add_symbols_btn.grid(row=0, column=3, padx=(10, 10), pady=(10, 10), sticky="nsew")


        # Scrollable Checkbox Symbols
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(master=self, command=self.checkbox_frame_event,
                                                                 item_list=[], width=280)
        self.scrollable_checkbox_frame.grid(row=2, rowspan=1, column=1, columnspan=3 ,padx=(10,10), pady=(0,0), sticky="nsew")

        # Search symbol entry
        self.search_bar_stocks = ctk.CTkEntry(self, placeholder_text = "Search (ex: TSLA)", width=180)
        self.search_bar_stocks.grid(row=1, column=1, columnspan=1, padx=(10, 0), pady=(10, 10), sticky="nsew")

        # Search symbol button
        self.search_symbols_btn = ctk.CTkButton(master=self, text="Search", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                 command=self.search_symbols, width=50)
        self.search_symbols_btn.grid(row=1, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # Correlate Button
        self.add_symbols_btn = ctk.CTkButton(master=self, text="Correlate", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                command=self.init_correlation, width=50)
        self.add_symbols_btn.grid(row=1, column=3, padx=(0, 10), pady=(10, 10), sticky="w")

        # Output text box
        self.output_textbox = ctk.CTkTextbox(self)
        self.output_textbox.grid(row = 3, column=1, columnspan=4, sticky = "nsew", padx=(10,10), pady=(10,10))

        # Create the plot figure and canvas
        self.plot_fig = Figure(figsize=(5,5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.plot_fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=4, rowspan=2, sticky = "nsew")

        # Create a toolbar and grid it onto the app
        toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        toolbar.grid(row=0, column=4)


    def init_correlation(self):
        
        if not(self.init_thread):
            self.init_thread = True
            self.t = th.Thread(target=self.stocks_data.init_metrics)
            self.t.start()
        

    def plot_price(self, symbols_plot):
        self.plot_fig.clf()
        ax = self.plot_fig.add_subplot(111)
        for i in range(len(symbols_plot)):
            for stock in self.stocks_data.stocks_array:
                if stock.symbol == symbols_plot[i]:
                    ax.plot(stock.close_data, label = symbols_plot[i])
        ax.legend(frameon=False)
        self.canvas.draw()
        return self.canvas.get_tk_widget()

    def add_stocks(self):
        print("Add Stocks")
        symbols_added = self.entry_stocks.get().split(", ")
        print(symbols_added)
        for symbol in symbols_added:
            print(symbol)
            if symbol not in self.symbols_lst:
                self.symbols_lst.append(symbol)
                self.stocks_data.add_stock(symbol)
        print(self.symbols_lst)
        self.scrollable_checkbox_frame.add_items(self.symbols_lst)

    def checkbox_frame_event(self):
        symbols_plot = self.scrollable_checkbox_frame.get_checked_items()
        print("Symbols plot :", symbols_plot)
        self.plot_price(symbols_plot)

    def search_symbols(self):
        string = self.search_bar_stocks.get()
        symbols = [symbol for symbol in self.symbols_lst if symbol == string or string in symbol]


if __name__ == "__main__":
    app = App()
    app.mainloop()