import os
import json
import pandas as pd
from pandas_datareader import data as pdr
import sqlite3
import datetime

#import csv
#import requests
#from bs4 import BeautifulSoup
#from selenium import webdriver
#import yfinance as yf
#import time


class getStockData:
    def __init__(self):
        self.stockdf = pd.read_csv(
            "https://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Basic+Industries&render=download",
            index_col=False)
        self.stockdf_Mexico = pd.read_csv(
            "https://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Basic+Industries&region=North+America&country=Mexico&render=download",
            index_col=False)
        self.stockdf_Canada = pd.read_csv(
            "https://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Basic+Industries&region=North+America&country=Canada&render=download",
            index_col=False)
        self.stockdf_NorthAmerican = pd.read_csv(
            "https://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Basic+Industries&region=North+America&render=download",
            index_col=False)
        self.stockSymbolJsonFile = None
        self.stockDatabase = sqlite3.connect('stock.db')

    def convertSymToJsonFile(self):  # in here symbo_list is dataframe
        '''
        Get returned list of stock symbol and saved into .json file
        At the same time get the list of stock symbol that are not American stock and save it to json format
        This step is for the convenience of sharing file with group and preparing for the further data cleaning step
        '''

        symbol_list = self.getStockSymbol(self.stockdf)
        non_USA_symbol = self.getNoneAmericanStockList()

        # Creating .json file for both none American and American stock
        cur_dir = os.getcwd()
        name = 'Stock_Symbols.json'
        name2 = 'None_USA_Stock_Symbols.json'
        json_path = os.path.join(cur_dir, name)
        json_path2 = os.path.join(cur_dir, name2)

        # update self.stockSymbolJsonFile and save symbols to corresponding file
        self.stockSymbolJsonFile = json_path
        symbol_list.to_json(json_path)
        non_USA_symbol.to_json(json_path2)


    def getStockSymbol(self,stockdf):
        '''
        Get stock symbol from the dataframe then filter out some undesired stock
        '''

        col = self.getColumnNames(stockdf)[0]   # return 'stock symbol'
        stock_symbol = stockdf[col]

        for idx, i in enumerate(stock_symbol):
            if i == 'ATISW' or i == 'HL^B' or i =='LEN.B' or i == 'SAND          ':
                stock_symbol = stock_symbol.drop([idx])
        return stock_symbol

    def getNoneAmericanStockList(self):
        '''
        This function is to help obtain the none USA stock,
        Since in North American stock symbol list there are only three country and for some reason nasdqp refuses
        to provide only USA stock info but provide only Canada and only Mexico stock info. So we get USA company from
        getting the company name of whole North American company list and remove the company names in Canada company list
        and the company names from Mexican company list. Then we use the whole company list to remove all the American
        company name to obtain a list of nonAmerican company names.
        '''

        # Get the stock symbol list to be filtered
        all_Stock_Symbol = self.getStockSymbol(self.stockdf)

        # Obtain NorthAmerican and Canada and Mexico company name lists
        col_Mexico = self.getColumnNames(self.stockdf_Mexico)[0]  # return 'stock symbol'
        stock_symbol_Mexico = self.stockdf_Mexico[col_Mexico]
        col_Canada = self.getColumnNames(self.stockdf_Canada)[0]  # return 'stock symbol'
        stock_symbol_Canada = self.stockdf_Canada[col_Canada]
        col_NorthAmerican = self.getColumnNames(self.stockdf_NorthAmerican)[0]  # return 'stock symbol'
        stock_symbol_NorthAmerican = self.stockdf_NorthAmerican[col_NorthAmerican]

        # Obtain American Company name list
        for idx, i in enumerate(stock_symbol_NorthAmerican):
            if i in stock_symbol_Mexico or i in stock_symbol_Canada:
                stock_symbol_NorthAmerican = stock_symbol_NorthAmerican.drop([idx])

        # Obtain non-American Company name list
        removeList = list(stock_symbol_NorthAmerican) +['ATISW', 'HL^B', 'LEN.B', 'SAND          ', 'VNTR', 'VRS', 'VSM', 'VVV']
        for i in removeList:
            if i in all_Stock_Symbol:
                loc = np.where(all_Stock_Symbol == i)
                all_Stock_Symbol = all_Stock_Symbol.drop([idx_j])

        none_USA_Symbol = all_Stock_Symbol
        return none_USA_Symbol

    def getColumnNames(self, stockdf):
        col_name_list = []
        for col in stockdf.columns:
            col_name_list += [col]
        return col_name_list

    def downloadDataToLocal(self):
        '''
        Helper function to download necessary data without looking over all the code
        '''
        self.convertSymToJsonFile()
        self.saveMultiCompany()

    def saveStockDataToLocal(self, company):
        '''
        Obtain up to date data using pandas_datareader module and save them into a location for further processing
        '''
        # Getting real time data
        year, month, day = self.getCurrentDate()
        # data = pdr.get_data_yahoo(company,start='{0}-{1}-{2}'.format(year-3, month, day), end='{0}-{1}-{2}'.format(year, month, day-1))
        data = pdr.get_data_yahoo(company, start = '2015-11-01', end='{0}-{1}-{2}'.format(year, month, day-1))

        # Creating File to save data
        dir_name = os.path.join(os.getcwd(), 'StockDataCSVFile')
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        file_name = '{}_Data.csv'.format(company)
        path = os.path.join(dir_name, file_name)

        # Save data to path
        data.to_csv(path)
        data.to_sql('{}_AllData'.format(company), self.stockDatabase, if_exists = 'replace')

    def getCurrentDate(self):
        '''
        Helper function to get current date
        '''
        currentDate = datetime.datetime.now()

        Year = currentDate.year
        Month = currentDate.month
        Day = currentDate.day
        return Year, Month, Day

    def saveMultiCompany(self):
        '''Helper function to iterate through all company to download .csv company stock pricing infromation file '''
        with open(self.stockSymbolJsonFile) as f:
            symbol_list = json.load(f)

        for key in symbol_list:
            company = symbol_list[key]
            self.saveStockDataToLocal(company)

    def accessCSV(self, company):
        '''Helper function to access each downloaded .csv company stock pricing infromation file '''
        dir_name = os.path.join(os.getcwd(), 'StockDataCSVFile')
        file_name = '{}_Data.csv'.format(company)
        path = os.path.join(dir_name, file_name)
        dataCSV = pd.read_csv(path)
        header = list(dataCSV.columns)
        return dataCSV

    def getCompanyStock(self, company):
        '''
        Obtain each company's closing price from sql database and organized them according to the date
        Use the date as the key of the json file dictionary for future access.
        '''

        c = self.stockDatabase.cursor()
        c.execute("SELECT ({col_name}) FROM {table}_AllData".format(col_name='Close', table=company))
        all_price = c.fetchall()
        c.execute("SELECT ({col_name}) FROM {table}_AllData".format(col_name='Date', table=company))
        all_date = c.fetchall()
        price_list = []

        # obtain close price by order in the sql file
        for i, price_row in enumerate(all_price):
            price_list = price_list + [price_row[0]]

        # obtain date by the same order as above
        company_stock_dict = {}
        for i, date_row in enumerate(all_date):
            company_stock_dict[date_row[0][0:10]] = price_list[i]

        # Create json file to save the newly formatted data
        dir_name = os.path.join(os.getcwd(), 'Price_Json_File')
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        # Save into individual json file
        price_json = 'price_{}.json'.format(company)
        json_path = os.path.join(dir_name, price_json)
        json.dump(company_stock_dict, open(json_path, 'w'))

    def MultiCompanyPrice(self):
        '''
        Iterate through all company name list to pass in all company names into function above.
        '''
        cur_dir = os.getcwd()
        name = 'Stock_Symbols.json'
        json_path = os.path.join(cur_dir, name)
        self.stockSymbolJsonFile = json_path

        with open(self.stockSymbolJsonFile) as f:
            symbol_list = json.load(f)

        for key in symbol_list:
            company = symbol_list[key]
            self.getCompanyStock(company)





    #def webScapeNASDAQ_only3monthdata(self):
    #    url = 'https://www.nasdaq.com/symbol/goog/historical'
    #    destination = os.getcwd()
    #    profile = webdriver.FirefoxProfile()
    #    profile.set_preference('browser.download.folderList', 2)  # custom location
    #    profile.set_preference('browser.download.manager.showWhenStarting', False)
    #    profile.set_preference('browser.download.dir', destination)
    #    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/plain, application/vnd.ms-excel, text/csv, text/comma-separated-values, application/octet-stream, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    #    driver = webdriver.Firefox(profile)
    #    driver.get(url)
    #    driver.find_element_by_id("lnkDownLoad").click()
    #    driver.close()

    #    return True

    #def webscrabYAHOO_doesntfullywork(self):
    #    self.url = 'https://query1.finance.yahoo.com/v7/finance/download/SPY?period1=1530891187&period2=1562427187&interval=1d&events=history&crumb=1Jx3OYxcHZ9'

    #    driver = webdriver.Firefox(profile)
    #    driver.get(self.url)

    #    html = driver.execute_script("return document.documentElement.outerHTML")
    #    soup = BeautifulSoup(html, 'html.parser')
    #    links_with_text = []
    #    for a in soup.find_all('a', href=True):
    #        if a.text == 'Download Data':

    #            print(a.text)
    #            file = requests.get(a['href']).text
    #            print(file)
    #            links_with_text.append(a['href'])
    #    print(links_with_text)

        #driver.find_element_by_id("lnkDownLoad").click()

        #continue_link = driver.find_element_by_partial_link_text('https://query1.finance.yahoo.com/v7/finance/download/GOOGL?period1=1404619200&period2=1562385600&interval=1d&events=history&crumb=sgYHBG54zT0')

        # file = requests.get(continue_link).tex
    #    driver.close()

    #def doesntwork(self):
    #    self.url1 = 'https://ca.finance.yahoo.com/quote/GOOGL/history?period1=1404619200&period2=1562385600&interval=1d&filter=history&frequency=1d'
    #    file = requests.get(self.url).text
    #    print(file)
    #    html = driver.execute_script("return document.documentElement.outerHTML")
    #    soup = BeautifulSoup(file, 'lxml')

    #    tableDiv = soup.find_all('INPUT')
    #    for link in tableDiv:
    #        print(link.get('href="/quote/GOOGL/financials?p=GOOGL"'))
    #        pass
    #    print(tableDiv)
    #    return True





