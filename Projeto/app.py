from unittest.util import _MAX_LENGTH
from stock_app import Stock

import pandas as pd #remover
import numpy as np
import itertools
from scipy.stats import pearsonr


from tksheet import Sheet
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

import collections

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

# Table for correlation heatmap
class UI_Table(tk.Tk):
    def __init__(self, main_window, **kw):
        self.table = Sheet(main_window)
        self.table.change_theme("dark")
        self.table.grid(row=0, column=0, sticky="nsew")
        self.heatmap_colors = ["#90083A", "#C93545", "#EE5F40", "#FAA15B", "#FED885", "#FEFDBA", "#E6EF92", "#A6D59E", "#63B99C", "#2D80B2", "#504A94"]
        self.heatmap_intervals = [-0.85, -0.75, -0.65, -0.45, -0.3, 0.3, 0.45, 0.65, 0.75, 0.85]
        self.n_colors = len(self.heatmap_colors)

    def update_columns(self, headers): #pode ser otimizado
        num_columns = len(self.table.headers())
        num_rows = self.table.get_total_rows()
        for i in range(num_rows):
            self.table.delete_row(idx = 0, deselect_all = False, redraw = True)
        for i in range(num_columns):
            self.table.delete_column(idx = 0)
        self.table.insert_columns(columns = len(headers), idx = "end", widths = None, deselect_all = False, add_rows = False, equalize_data_row_lengths = True,
                   mod_column_positions = True,
                   redraw = False)
        self.table.headers((f"{c}" for c in headers))       

    def insert_row(self, data):
        self.table.insert_row(values=data)

    def update_index(self):
        self.table.row_index(newindex = self.table.headers(), index = None, reset_row_positions = False, show_index_if_not_sheet = True, redraw = False)

    # color the table
    def heat_map(self):
        num_columns = len(self.table.headers())
        num_rows = self.table.get_total_rows()
        for i in range(num_rows):
            for j in range(num_columns):
                value = float(self.table.get_cell_data(i, j, return_copy = True))
                idx = self.n_colors - 1
                for k in range(len(self.heatmap_intervals)):
                    if value < self.heatmap_intervals[k]:
                        idx = k
                        break
                self.table.highlight_cells(row = i, column = j, cells = [], canvas = "table", bg = self.heatmap_colors[idx], fg = "#19191E", redraw = False, overwrite = True)

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.n_ticks = 30
        Stock.n_sticks = self.n_ticks
        self.init_thread = False
        self.add_thread = False
        self.update_stocks_thread = False
        self.symbols_lst = []
        self.stocks_array = []
        self.n_symbols = 0
        self.n_stocks_added = 0
        self.textbox_n_lines = 0
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
        self.correlate_btn = ctk.CTkButton(master=self.home_frame, text="Correlate", fg_color="transparent", border_width=2,
                                          text_color=("gray10", "#DCE4EE"), width=50)

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
        self.correlations_frame.rowconfigure(0, weight=1)

        self.correlations_table = UI_Table(self.correlations_frame)

        # Side bar anomalies button
        self.anomalies_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Anomalies",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.anomalies_button_event)
        
        self.anomalies_button.grid(row=2, column=0, sticky="ew")
        # Anomalies frame
        self.anomalies_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.anomalies_frame.rowconfigure(0, weight=0)
        self.anomalies_frame.columnconfigure((0,1), weight=0)
        self.anomalies_frame.columnconfigure(2, weight=1)
        # Combo boxes to select stock anomalies
        self.combobox_1 = ctk.CTkComboBox(self.anomalies_frame, command=self.combobox_callback, width=120)
        self.combobox_1.grid(row=0, column = 0, padx=(10,10), pady=(10,10))
        self.combobox_2 = ctk.CTkComboBox(self.anomalies_frame, command=self.combobox_callback, width=120)
        self.combobox_2.grid(row=0, column = 1, pady=(10,10))

        # Anomalies plot
        self.anomalies_plot_fig = Figure(figsize=(5,5), dpi=100)
        self.anomalies_plot_fig.patch.set_facecolor('#242424')
        self.anomalies_canvas = FigureCanvasTkAgg(self.anomalies_plot_fig, master=self.anomalies_frame)
        self.anomalies_canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, sticky = "nsew")

        # Start the app on the home frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.correlations_button.configure(fg_color=("gray75", "gray25") if name == "correlations" else "transparent")
        self.anomalies_button.configure(fg_color=("gray75", "gray25") if name == "anomalies" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row = 0, rowspan=4, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "correlations":
            self.correlations_frame.grid(row=0, rowspan=4, column=1, sticky="nsew")
        else:
            self.correlations_frame.grid_forget()
        if name == "anomalies":
            self.anomalies_frame.grid(row=0, rowspan=4, column=1, sticky="nsew")
        else:
            self.anomalies_frame.grid_forget()

    # Function triggered by the frame home button
    def home_button_event(self):
        self.select_frame_by_name("home")

    # Function triggered by the frame correlations_button
        # It will add columns and rows to the correlation table
    def correlations_button_event(self):
        if (not self.add_thread) and (not self.update_stocks_thread) and (not self.init_thread):
            self.correlations_table.update_columns(self.symbols_lst)
            for stock in self.stocks_array:
                correlation_data = [ '%.2f' % elem for elem in stock.correlation ]
                self.correlations_table.insert_row(correlation_data)
            self.correlations_table.update_index()
            self.correlations_table.heat_map()
            self.select_frame_by_name("correlations")

    def anomalies_button_event(self):
        combobox_var1 = ctk.StringVar(value=self.stocks_array[0].symbol)  # set initial value
        self.combobox_1.configure(values=[stock.symbol for stock in self.stocks_array], variable=combobox_var1)
        if self.n_symbols <= 1:
            self.combobox_2.configure(values=[stock.symbol for stock in self.stocks_array], variable=combobox_var1)
        else:
            combobox_var2 = ctk.StringVar(value=self.stocks_array[1].symbol)  # set initial value
            self.combobox_2.configure(values=[stock.symbol for stock in self.stocks_array], variable=combobox_var2)
        self.select_frame_by_name("anomalies")

    # Function to get combo boxes Symbols
    def combobox_callback(self, choice):
        symbol_1 = self.combobox_1.get()
        symbol_2 = self.combobox_2.get()
        if symbol_1 != symbol_2:
            labels, index_1, index_2 = self.iqr_anomaly_detector(symbol_1, symbol_2)
            self.plot_anomalies(labels, self.stocks_array[index_1].correlations_history[index_2], symbol_1, symbol_2)

    # Create the plot graphic for anomalies
    def plot_anomalies(self, labels, values, symbol_1, symbol_2):
        self.anomalies_plot_fig.clf()
        ax = self.anomalies_plot_fig.add_subplot(111)
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        colors = ['g' if l == 0 else 'r' for l in labels]
        x = [value for value in range(Stock.n_windows)]
        ax.scatter(x, values, c = colors)
        ax.legend(frameon=False)
        ax.set_facecolor('#2B2B2B')
        ax.set_title(symbol_1 + " and " + symbol_2 + " correlation anomalies")
        ax.set_xlabel("Days")
        ax.set_ylabel("Correlation")
        self.anomalies_canvas.draw()
        return self.anomalies_canvas.get_tk_widget()

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
        ax.set_title("Rentability")
        ax.set_xlabel("Days")
        ax.set_ylabel("Log(Value)")
        self.canvas.draw()
        return self.canvas.get_tk_widget()

    # Function triggered by the Add button 
        # Add stocks the the list
        # Create the stock object
    def add_stocks_event(self):
        if (not self.add_thread) and (not self.update_stocks_thread) and (not self.init_thread):
            self.add_thread = True
            t_add = th.Thread(target=self.add_stocks)
            t_add.setDaemon(True)
            t_add.start()
            t_corr = th.Thread(target=self.init_correlation)
            t_corr.setDaemon(True)
            t_corr.start()

    # Checks if the stock is in list
        #Adds the stocks to the scrollable frame
    def add_stocks(self):
        print("Add Stocks")
        symbols_added = self.entry_stocks.get().replace(";", ",").replace(" ", "").split(",")
        print(symbols_added)
        self.n_stocks_added = 0
        for symbol in symbols_added:
            if symbol not in self.symbols_lst:
                self.n_stocks_added += self.add_stock(symbol)
        self.scrollable_checkbox_frame.add_items(self.symbols_lst)
        self.add_thread = False

    # Add and creates the stock object
    def add_stock(self, symbol):
        self.n_symbols += 1
        Stock.n_stocks = self.n_symbols
        try:
            stock = Stock(symbol)
            self.stocks_array.append(stock)
            self.symbols_lst.append(symbol)
            for i in range(self.n_symbols-1):    
                self.stocks_array[i].add_corr_space()
            return 1                                                # success
        except ValueError as e:                                     # If there's an error it shows the error to the user
            self.n_symbols -= 1
            Stock.n_stocks = self.n_symbols
            #self.output_textbox.configure(state="normal")
            #self.output_textbox.insert(ctk.END, str(e))
            #self.output_textbox.configure(state="disabled")
            self.insert_text(str(e))
            return 0                                                # failure
                  
    # Function triggered by the correlationn button
    def init_correlation(self):
        while (self.add_thread or self.update_stocks_thread or self.init_thread):
            time.sleep(1)
        self.init_thread = True
        self.init_metrics()
        #self.output_textbox.configure(state="normal")
        #self.output_textbox.insert(ctk.END, "The correlation is finished\n")
        #self.output_textbox.configure(state="disabled")
        self.insert_text("The correlation is finished\n")
        self.init_thread = False

    # Calculates the correlation of stocks
    def init_metrics(self):
        for i in range(self.n_symbols):
            if i < (self.n_symbols-self.n_stocks_added):
                self.stocks_array[i].set_index(0)
            for j in range(self.n_symbols-self.n_stocks_added, self.n_symbols):
                print("ij: ", i,j)
                if j >= i:
                    self.calc_correlation(i,j,0)
            print("correlation_history: ", self.stocks_array[i].correlations_history)

        for k in range(1, Stock.n_windows):                                           #calculate the correlations
            for i in range(self.n_symbols-self.n_stocks_added, self.n_symbols):
                self.stocks_array[i].update_metrics(k)
            for i in range(self.n_symbols):
                self.stocks_array[i].set_index(k) #fazer apenas quando nas stocks antigas
                for j in range(self.n_symbols-self.n_stocks_added, self.n_symbols):
                    if j>=i:
                        self.calc_correlation(i,j,k)
            print(k)

        for i in range(self.n_symbols):
            self.stocks_array[i].set_last_correlation()

    def calc_correlation(self,i,j,k):
        if i == j:
            self.stocks_array[i].correlations_history[j].append(1)
        else:
            result, index = self.stocks_array[i].calc_correlation(j, self.stocks_array[j].get_deviations(), self.stocks_array[j].std_dev[k], k)
            self.stocks_array[j].correlations_history[i].append(self.stocks_array[i].correlations_history[j][k])
            if result == 1:                                 # Tells the user that the values of a stock remained static
                #self.output_textbox.configure(state="normal")
                if index == -1:
                    #self.output_textbox.insert(ctk.END, "The close values of " + self.symbols_lst[i] + " are exactly the same over the time period\n")
                    self.insert_text("The close values of " + self.symbols_lst[i] + " are exactly the same over the time period\n")
                else:
                    #self.output_textbox.insert(ctk.END, "The close values of " + self.symbols_lst[j] + " are exactly the same over the time period\n")
                    self.insert_text("The close values of " + self.symbols_lst[j] + " are exactly the same over the time period\n")
                #self.output_textbox.configure(state="disabled")
        x = list(itertools.islice(self.stocks_array[i].rentability, k, Stock.n_ticks-1+k))
        y = list(itertools.islice(self.stocks_array[j].rentability, k, Stock.n_ticks-1+k))
        z, _ = pearsonr(x, y)
        print(z,":", self.stocks_array[i].correlations_history[j][k])

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
            while ((self.add_thread != False) or (self.init_thread != False)):
                print("Sleeping")
                time.sleep(1)
            self.update_stocks_thread = True
            for stock in self.stocks_array:
                try:
                    status = stock.check_market_status()            # check the if the market changed from close->open or open->close
                    print(status)
                    if status == 0:
                        #self.output_textbox.configure(state="normal")
                        #self.output_textbox.insert(ctk.END, "Updated the value of the Stock " + stock.symbol + ", (" + str(stock.close_data[0])+ "," + str(stock.close_data[self.n_ticks-1]) + ")")
                        #stock.update_metrics_realtime()
                        #self.output_textbox.insert(ctk.END, " -> (" + str(stock.close_data[0]) + "," + str(stock.close_data[self.n_ticks-1]) + ")\n")
                        #self.output_textbox.configure(state="disabled")
                        self.insert_text("Updated the value of the Stock " + stock.symbol + ", (" + str(stock.close_data[0])+ "," + str(stock.close_data[self.n_ticks-1]) + ")")
                        stock.update_metrics_realtime()
                        self.insert_text( " -> (" + str(stock.close_data[0]) + "," + str(stock.close_data[self.n_ticks-1]) + ")\n")
                except ValueError as e:  
                    self.insert_text(str(e))
                    #self.output_textbox.configure(state="normal")
                    #self.output_textbox.insert(ctk.END, str(e))
                    #self.output_textbox.configure(state="disabled")

            for i in range(self.n_symbols):
                for j in range(i, self.n_symbols):
                    self.calc_correlation(i,j,Stock.n_windows-1)

            for i in range(self.n_symbols):
                for j in range(i+1, self.n_symbols):
                    labels, index_1, index_2 = self.iqr_anomaly_detector(self.symbols_lst[i],self.symbols_lst[j])
                    if labels[-1] == 1:
                        tk.messagebox.showinfo("Anomaly","Anomaly on the correlation of stocks: " + self.symbols_lst[i] + " and " + self.symbols_lst[j])

            
    # Removes stock from lists
    def remove_stock(self, idx):
        self.symbols_lst.pop(idx)                                   # Remove symbol from the list
        self.stocks_array.pop(idx)                                  # Remove the stock from the stock_array
        self.n_symbols -= 1                                         # Update the number of symbols
        Stock.n_stocks = self.n_symbols                             # Update the number of stocks on the Stock class
        for i in range(self.n_symbols):                             # Remove the other stocks correlations with the stock removed
            self.stocks_array[i].correlation.pop(idx)
            self.stocks_array[i].correlations_history.pop(idx)

    def insert_text(self,text):
        self.output_textbox.configure(state="normal")
        if self.textbox_n_lines > 10:
            contents = self.output_textbox.get('1.0', 'end')
            lines = contents.split('\n')
            del lines[0]
            if lines[-1] == '':
                del lines[-1]
            line_end_index = self.output_textbox.index('1.end')
            new_contents = '\n'.join(lines)
            self.output_textbox.delete('1.0', 'end')
            self.output_textbox.insert('1.0', new_contents)
            #self.output_textbox.delete("1.0", line_end_index)
            self.textbox_n_lines -= 1
        self.output_textbox.insert(ctk.END, text)
        self.output_textbox.configure(state="disabled")
        self.textbox_n_lines += 1


    #  Label anomalies
    def find_anomalies(self, value, lower_threshold, upper_threshold):
        if value < lower_threshold or value > upper_threshold:
            return 1
        else: 
            return 0

    # Interquartile range for anomalies
    def iqr_anomaly_detector(self, symbol_1, symbol_2, threshold=0.5):
        index_1 = self.symbols_lst.index(symbol_1)
        index_2 = self.symbols_lst.index(symbol_2)
        idx_quartile_1 = int(Stock.n_windows*0.25)
        idx_quartile_3 = int(Stock.n_windows*0.75)
        sorted_data = list(collections.deque(self.stocks_array[index_1].correlations_history[index_2]))
        sorted_data.sort()
        quartile_1 = sorted_data[idx_quartile_1]
        quartile_3 = sorted_data[idx_quartile_3]
        iqr = quartile_3 - quartile_1

        lower_threshold = quartile_1 - (threshold * iqr)
        upper_threshold = quartile_3 + (threshold * iqr)

        labels = [self.find_anomalies(value, lower_threshold, upper_threshold) for value in self.stocks_array[index_1].correlations_history[index_2]]
        return labels, index_1, index_2
        
        

if __name__ == "__main__":
    app = App()
    app.mainloop()