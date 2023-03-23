from stocks_data import Stocks_data
from stock_app import Stock

import threading as th
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import customtkinter as ctk

import time
import os
import requests
import bs4
from PIL import Image # To use images on the app


import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Info_window(ctk.CTkToplevel):

    def __init__(self, symbol):
        super().__init__()
        self.title("Info " + symbol)
        self.geometry(f"{720}x{580}")
        self.grid_rowconfigure((0,1,2,3,4), weight = 0)
        self.grid_rowconfigure(5, weight = 1)
        self.grid_columnconfigure(0, weight=1)

        self.company_label = ctk.CTkLabel(self, text="Name: ", font=ctk.CTkFont(size=20, weight="bold"))
        self.company_label.grid(row=0, column=0, padx=(10,10), pady=(10, 10), sticky = "w")

        self.symbol_label = ctk.CTkLabel(self, text=("Stock symbol: " + symbol), font=ctk.CTkFont(size=18, weight="bold"))
        self.symbol_label.grid(row=1, column=0, padx=(10,10), pady=(0, 10), sticky = "w")
        
        self.sectors_label = ctk.CTkLabel(self, text="Sector: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.sectors_label.grid(row=2, column=0, padx=(10,10), pady=(0, 10), sticky = "w")

        self.industry_label = ctk.CTkLabel(self, text="Industry: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.industry_label.grid(row=3, column=0, padx=(10,10), pady=(0, 10), sticky = "w")

        self.description_text_label = ctk.CTkLabel(self, text="Description: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.description_text_label.grid(row=4, column=0, padx=(10,10), pady=(0, 10), sticky = "w")

        self.description_text = ctk.CTkTextbox(self, font=ctk.CTkFont(size=14))
        self.description_text.grid(row = 5, column=0, sticky = "nsew", padx=(10,10), pady=(0,10))

        self.webscrape_info(symbol)

    # Get webpage source code
    def webscrape_page(self, symbol):
        url = "https://finance.yahoo.com/quote/" + symbol + "/profile?p=" + symbol
        """Download a webpage and return a beautiful soup doc"""
        response = requests.get(url, headers={'User-Agent': 'Custom'}) # to try and pass as a person accessing the website
        if not response.ok:
            print('Status code:', response.status_code)
            raise Exception('Failed to load page {}'.format(url))
        page_content = response.text
        doc = bs4.BeautifulSoup(page_content, 'html.parser')
        return doc

    def webscrape_info(self, symbol):
        doc = self.webscrape_page(symbol)
        text = doc.find("h1", class_= "D(ib) Fz(18px)")
        self.company_label.configure(text=text.text)

        text = doc.find_all("span", class_= "Fw(600)")
        self.sectors_label.configure(text=("Sector: " + text[1].text))
        self.industry_label.configure(text=("Industry: " + text[2].text))
        text = doc.find("p", class_= "Mt(15px) Lh(1.6)").text
        self.description_text.insert("0.0", (text + "\n"))
        self.description_text.configure(state="disabled")

class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.checkbox_list = []
        self.info_btn_lst = []
        self.remove_btn_lst = []
        self.items_lst =[]
        self.prev_checked_items = []
        self.info_window = None

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
        info_btn = ctk.CTkButton(master=self, text="Info", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), width=80, command=lambda: self.show_item_info(item))
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
        if (not app.add_thread):                                       # Manage threads, if it's adding stocks it shouldn't remove since it may crash the a++
            checked_items = self.get_checked_items()                # Get the boxes that are checked
            for i in range(len(self.checkbox_list)):                    # Iterate trough the items
                if item == self.checkbox_list[0].cget("text"):          # Check if it's the item we want to remove
                    print(self.items_lst)
                    print(i, "Removi :", item)
                    idx = self.items_lst.index(item)
                    self.items_lst.pop(idx)                             # Remove the item
                    self.prev_checked_items.pop(idx)
                    app.remove_stock(idx)
                
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
                app.plot_rentability(checked_items)
            return

    # Search for items in the list
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

    # Return of a list with the checked items
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

    def show_item_info(self, item):
        if self.info_window is None or not self.info_window.winfo_exists():
            self.info_window = Info_window(item)
            self.info_window.focus()
        else:
            self.info_window.focus()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.n_ticks = 60
        Stock.n_sticks = self.n_ticks
        self.init_thread = False
        self.add_thread = False
        self.update_stocks_thread = False
        self.symbols_lst = []
        self.stocks_array = []
        self.n_symbols = 0
        background_update_thread = th.Thread(target=self.background_close_value_update)
        background_update_thread.setDaemon(True)
        background_update_thread.start()

        # Images
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.home_logo_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_logo.png")), size=(20, 20))

        # Configure window
        self.title("Financial Markets")
        self.geometry(f"{1100}x{580}")

        # Configure grid
            # weight = 0 fixo
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1), weight=0)

        # Side bar frame
        self.navigation_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)


        # Side bar home button
        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_logo_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=0, column=0, sticky="ew")

        # Home frame
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(3, weight=1)
        self.home_frame.grid_rowconfigure((2, 3), weight=1)
        self.home_frame.grid_rowconfigure((0, 1), weight=0)

        # Symbols entry
        self.entry_stocks = ctk.CTkEntry(self.home_frame, placeholder_text = "Stocks (ex: TSLA, AMZN, META)", width=230)
        self.entry_stocks.grid(row=0, column=0, columnspan=2, padx=(10, 0), pady=(10, 10), sticky="nsew")
            
        # Symbols entry button
        self.add_symbols_btn = ctk.CTkButton(self.home_frame, text="Add", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                command=self.add_stocks_event, width=50)
        self.add_symbols_btn.grid(row=0, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew")


        # Scrollable Checkbox Symbols
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(self.home_frame, command=self.checkbox_frame_event,
                                                                 item_list=[], width=280)
        self.scrollable_checkbox_frame.grid(row=2, rowspan=1, column=0, columnspan=3 ,padx=(10,10), pady=(0,0), sticky="nsew")

        # Search symbol entry
        self.search_bar_stocks = ctk.CTkEntry(self.home_frame, placeholder_text = "Search (ex: TSLA)", width=180)
        self.search_bar_stocks.grid(row=1, column=0, columnspan=1, padx=(10, 0), pady=(10, 10), sticky="nsew")

        # Search symbol button
        self.search_symbols_btn = ctk.CTkButton(self.home_frame, text="Search", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                 command=self.search_symbols, width=50)
        self.search_symbols_btn.grid(row=1, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # Correlate Button
        self.correlate_btn = ctk.CTkButton(master=self.home_frame, text="Correlate", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                command=self.init_correlation, width=50)
        self.correlate_btn.grid(row=1, column=2, padx=(0, 10), pady=(10, 10), sticky="w")

        # Output text box
        self.output_textbox = ctk.CTkTextbox(self.home_frame)
        self.output_textbox.configure(state="disabled")
        self.output_textbox.grid(row = 3, column=0, columnspan=4, sticky = "nsew", padx=(10,10), pady=(10,10))

        # Create the plot figure and canvas
        self.plot_fig = Figure(figsize=(5,5), dpi=100)
        self.plot_fig.patch.set_facecolor('#242424')
        self.canvas = FigureCanvasTkAgg(self.plot_fig, master=self.home_frame)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=2, sticky = "nsew")
        color = 'white'
        matplotlib.rcParams['text.color'] = color
        matplotlib.rcParams['axes.labelcolor'] = color
        matplotlib.rcParams['xtick.color'] = color
        matplotlib.rcParams['ytick.color'] = color

        # Create a toolbar and grid it onto the app
        toolbar = NavigationToolbar2Tk(self.canvas, self.home_frame, pack_toolbar=False)
        toolbar.grid(row=0, column=3)
        #toolbar.setStyleSheet("background-color:Gray14;")
        toolbar.config(bg='#242424')
        toolbar._message_label.config(background='#242424')
        toolbar._message_label.config(foreground='#FFFFFF')
        toolbar.update()
        # Side bar correlations button
        self.correlations_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Correlations",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.correlations_button_event)
        self.correlations_button.grid(row=1, column=0, sticky="ew")

        # Correlations frame
        self.correlations_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.correlations_frame.columnconfigure(0, weight=1)
        self.correlations_frame.columnconfigure(1, weight=0)
        self.correlations_frame.rowconfigure(0, weight=1)
        self.correlations_frame.rowconfigure(1, weight=0)

        self.correlations_table = ttk.Treeview(self.correlations_frame, show="headings")
        self.correlations_table.grid(row=0, column=0, sticky="nsew")
        # Create the Scrollbars
        yscrollbar = ttk.Scrollbar(self.correlations_frame, orient='vertical', command=self.correlations_table.yview)
        xscrollbar = ttk.Scrollbar(self.correlations_frame, orient='horizontal', command=self.correlations_table.xview)
        self.correlations_table.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        yscrollbar.grid(row=0, column=1, sticky='ns')
        xscrollbar.grid(row=1, column=0, sticky='ew')
        style = ttk.Style()
    
        style.theme_use("default")

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="#FFFFFF",
                        relief="flat")
        style.map("Treeview.Heading",
                    background=[('active', '#565b5e')])

        style.configure("Treeview",
                        background="#FFFFFF",
                        foreground="#2a2d2e",
                        rowheight=25,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#8694EE')])


        # Start the app on the home frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.correlations_button.configure(fg_color=("gray75", "gray25") if name == "correlations" else "transparent")
        #self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row = 0, rowspan=4, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "correlations":
            self.correlations_frame.grid(row=0, rowspan=4, column=1, sticky="nsew")
            self.correlations_table.grid(row=0, column=0, sticky="nsew")
        else:
            self.correlations_frame.grid_forget()

    # Function triggered by the frame home button
    def home_button_event(self):
        self.select_frame_by_name("home")

    # Function triggered by the frame correlations_button
        # It will add columns and rows to the correlation table
    def correlations_button_event(self):
        # Get a list of all the row identifiers
        rows = self.correlations_table.get_children()
        # Delete each row
        for row in rows:
            self.correlations_table.delete(row)
        # Get the current columns
        columns = self.correlations_table['columns']
        # Delete the current columns
        for col in columns:
            self.correlations_table.column(col, width=0)
            self.correlations_table.heading(col, text="")
        # Insert columns
        columns = [stock.symbol for stock in self.stocks_array]
        columns.insert(0, "Symbols")
        self.correlations_table["columns"] = columns
        for i, col in enumerate(columns):
            self.correlations_table.column(col, width=100)
            self.correlations_table.heading(col, text=col, anchor="w")
        self.correlations_table.column("Symbols", width=70, minwidth=70, anchor="w")
        # Insert rows
        for stock in self.stocks_array:
            corr = stock.correlation.copy()
            corr.insert(0, stock.symbol)
            self.correlations_table.insert("", "end", values = corr)
        # Select frame
        self.select_frame_by_name("correlations")

    # Function triggered by the correlationn button
    def init_correlation(self):
        if (not self.add_thread) and (not self.update_stocks_thread) and (not self.init_thread):
            self.init_thread = True
            t = th.Thread(target=self.init_metrics)
            t.setDaemon(True)
            t.start()
            self.output_textbox.configure(state="normal")
            self.output_textbox.insert(ctk.END, "The correlation is finished\n")
            self.output_textbox.configure(state="disabled")
            self.init_thread = False
        
    # Create the plot graphic
    def plot_rentability(self, symbols_plot):
        self.plot_fig.clf()
        ax = self.plot_fig.add_subplot(111)
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        for i in range(len(symbols_plot)):
            for stock in self.stocks_array:
                if stock.symbol == symbols_plot[i]:
                    ax.plot(stock.rentability, label = symbols_plot[i])
        ax.legend(frameon=False)
        ax.set_facecolor('#2B2B2B')
        self.canvas.draw()
        self.plot_fig.suptitle("Rentability")
        self.plot_fig.supxlabel("Days")
        self.plot_fig.supylabel("Log(Value)")
        return self.canvas.get_tk_widget()

    # Function triggered by the Add button 
        # Add stocks the the list
        # Create the stock object
    def add_stocks_event(self):
        if (not self.add_thread) and (not self.update_stocks_thread) and (not self.init_thread):
            self.add_thread = True
            t = th.Thread(target=self.add_stocks)
            t.setDaemon(True)
            t.start()

    # Checks if the stock is in list
        #Adds the stocks to the scrollable frame
    def add_stocks(self):
        print("Add Stocks")
        symbols_added = self.entry_stocks.get().split(", ")
        print(symbols_added)
        for symbol in symbols_added:
            if symbol not in self.symbols_lst: #pop de stocks que já estão altero o tamanho da stock_data
                self.add_stock(symbol)
        self.scrollable_checkbox_frame.add_items(self.symbols_lst)
        self.add_thread = False

    # Check add_thread status (######################## not used ????)
    def check_add_thread_status(self, thread):
        if thread.is_alive():
            self.after(100, self.check_thread_status, thread)

    # Function that updates the plot every time an item is checked
    def checkbox_frame_event(self):
        symbols_plot = self.scrollable_checkbox_frame.get_checked_items()
        print("Symbols plot :", symbols_plot)
        self.plot_rentability(symbols_plot)

    # Function that search symbols on the stock list
    def search_symbols(self):
        string = self.search_bar_stocks.get()
        symbols = [symbol for symbol in self.symbols_lst if symbol == string or string in symbol]
        print("Symbols searched :", symbols)
        self.scrollable_checkbox_frame.search_items(symbols)

    # Does the background calculus
    def background_close_value_update(self):
        while True:
            current_time = time.localtime()  # get current time
            min_til = 30 - current_time.tm_min % 30
            sec_til = (min_til * 60 - current_time.tm_sec)
            self.update_stocks_thread = False
            print("Minutes till next update: " + str(min_til))
            time.sleep(sec_til)
            while ((self.add_thread != False) and (self.init_thread != False)):
                print("Sleeping")
                time.sleep(1)
            self.update_stocks_thread = True
            for stock in self.stocks_array:
                try:
                    status = stock.check_market_status()            # check the if the market changed from close->open or open->close
                    print(status)
                    if status == 0:
                        self.output_textbox.configure(state="normal")
                        self.output_textbox.insert(ctk.END, "Updated the value of the Stock " + stock.symbol + ", (" + str(stock.close_data[0])+ "," + str(stock.close_data[self.n_ticks-1]) + ")")
                        stock.update_data()
                        self.output_textbox.insert(ctk.END, " -> (" + str(stock.close_data[0]) + "," + str(stock.close_data[self.n_ticks-1]) + ")\n")
                        self.output_textbox.configure(state="disabled")
                except ValueError as e:  
                        self.output_textbox.configure(state="normal")
                        self.output_textbox.insert(ctk.END, str(e))
                        self.output_textbox.configure(state="disabled")
            

    # Removes stock from lists
    def remove_stock(self, idx):
        self.symbols_lst.pop(idx)                                   # Remove symbol from the list
        self.stocks_array.pop(idx)                                  # Remove the stock from the stock_array
        self.n_symbols -= 1                                         # Update the number of symbols
        Stock.n_stocks = self.n_symbols                             # Update the number of stocks on the Stock class
        for i in range(self.n_symbols):                             # Remove the other stocks correlations with the stock removed
            self.stocks_array[i].correlation.pop(idx)

    # Add and creates the stock object
    def add_stock(self, symbol):
        self.n_symbols += 1
        Stock.n_stocks = self.n_symbols
        try:
            stock = Stock(symbol)
            self.stocks_array.append(stock)
            self.symbols_lst.append(symbol)
            for i in range(self.n_symbols-1):    
                self.stocks_array[i].correlation.append(0)    
            return 0
        except ValueError as e:                                     # If there's an error it shows the error to the user
            self.n_symbols -= 1
            Stock.n_stocks = self.n_symbols
            self.output_textbox.configure(state="normal")
            self.output_textbox.insert(ctk.END, str(e))
            self.output_textbox.configure(state="disabled")
            return str(e)
                  
    # Calculates the correlation of stocks
    def init_metrics(self):
        for i in range(self.n_symbols):
            self.stocks_array[i].init_metrics()
        for i in range(self.n_symbols):
            for j in range(i, self.n_symbols):
                if i == j:
                    self.stocks_array[i].correlation[j] = 1
                else:
                    result = self.stocks_array[i].calc_correlation(j, self.stocks_array[j].deviations, self.stocks_array[j].std_dev)
                    self.stocks_array[j].correlation[i] = self.stocks_array[i].correlation[j]
                    if result == 1:                                 # Tells the user that the values of a stock remained static
                        self.output_textbox.configure(state="normal")
                        self.output_textbox.insert(ctk.END, "The close values of " + self.symbols_lst[i] + "are exactly the same over the time period\n")
                        self.output_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()