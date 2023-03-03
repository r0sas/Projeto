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
        self.prev_checked_items = []


        for i, item in enumerate(item_list):
            self.add_item(item)

    # Add items to the list
    def add_items(self, items):
        for item in items:
            if item not in self.items_lst:
                self.create_list_item(item)
                self.items_lst.append(item)
                self.prev_checked_items.append(0)
                print("Added: ", item)

    # Create the items widgets
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

    # Remove button
    def remove_item(self, item):
        checked_items = self.get_checked_items()                # Get the boxes that are checked

        for i in range(len(self.checkbox_list)):                    # Iterate trough the items
            if item == self.checkbox_list[0].cget("text"):          # Check if it's the item we want to remove
                print(self.items_lst)
                print(i, "Removi :", item)
                idx = self.items_lst.index(self.checkbox_list[0].cget("text"))
                self.items_lst.pop(idx)                             # Remove the item
                self.prev_checked_items.pop(idx)
                
            self.checkbox_list[0].destroy()                     # Destroy all the widgets
            self.info_btn_lst[0].destroy()                          #
            self.remove_btn_lst[0].destroy()                        #
            self.info_btn_lst.pop(0)                                #
            self.remove_btn_lst.pop(0)                              #
            self.checkbox_list.pop(0)                               #
            
        self.update_items()                                     # Build all the widgets 
        for checkbox in self.checkbox_list:                     # Check all the items that were previously checked
            if checkbox.cget("text") in checked_items:
                checkbox.select()
        if item in checked_items:                               # If the item we removed was checked we need to make the plot again
            checked_items.remove(item)            
            app.plot_price(checked_items)
        return

    def search_items(self, items):
        symbols_plot = self.get_checked_items()
        for i in range(len(self.checkbox_list)):
            self.checkbox_list[0].destroy()                     # Destroy all the widgets
            self.info_btn_lst[0].destroy()                          #
            self.remove_btn_lst[0].destroy()                        #
            self.info_btn_lst.pop(0)                                #
            self.remove_btn_lst.pop(0)                              #
            self.checkbox_list.pop(0)                               #
        for i in range(len(items)):
            self.create_list_item(items[i])
            if items[i] in symbols_plot:
                self.checkbox_list[i].select()

    # return de lista com items com check
    def get_checked_items(self):
        if len(self.checkbox_list) < len(self.items_lst):
            items_checked = [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]
            items_unchecked = [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 0]
            indexes_c = [idx for idx, symbol in enumerate(self.items_lst) if symbol in items_checked]
            indexes_u = [idx for idx, symbol in enumerate(self.items_lst) if symbol in items_unchecked]
            for idx in indexes_c:
                self.prev_checked_items[idx] = 1
            for idx in indexes_u:
                self.prev_checked_items[idx] = 0
            return [self.items_lst[i] for i in range(len(self.items_lst)) if self.prev_checked_items[i] == 1]

        else:
            check_items = [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]
            self.prev_checked_items = [1 if item in check_items else 0 for item in self.items_lst]
            return check_items


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
        
    # Create the plot graphic
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

    # Add stocks the the list
    # Create the stock object
    def add_stocks(self):
        print("Add Stocks")
        symbols_added = self.entry_stocks.get().split(", ")
        print(symbols_added)
        for symbol in symbols_added:
            if symbol not in self.symbols_lst:
                self.symbols_lst.append(symbol)
                self.stocks_data.add_stock(symbol)
        self.scrollable_checkbox_frame.add_items(self.symbols_lst)

    # Function that updates the plot every time an item is checked
    def checkbox_frame_event(self):
        symbols_plot = self.scrollable_checkbox_frame.get_checked_items()
        print("Symbols plot :", symbols_plot)
        self.plot_price(symbols_plot)

    # Function that search symbols on the stock list
    def search_symbols(self):
        string = self.search_bar_stocks.get()
        symbols = [symbol for symbol in self.symbols_lst if symbol == string or string in symbol]
        print("Symbols searched :", symbols)
        self.scrollable_checkbox_frame.search_items(symbols)
        


if __name__ == "__main__":
    app = App()
    app.mainloop()