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
import yfinance as yf
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
        symbol_list = self.getStockSymbol(self.stockdf)
        non_USA_symbol = self.getNoneAmericanStockList()
        cur_dir = os.getcwd()
        name = 'Stock_Symbols.json'
        name2 = 'None_USA_Stock_Symbols.json'
        json_path = os.path.join(cur_dir, name)
        json_path2 = os.path.join(cur_dir, name2)

        self.stockSymbolJsonFile = json_path
        symbol_list.to_json(json_path)
        non_USA_symbol.to_json(json_path2)

    def getStockSymbol(self,stockdf):
        col = self.getColumnNames(stockdf)[0]   # return 'stock symbol'
        stock_symbol = stockdf[col]

        for idx, i in enumerate(stock_symbol):
            if i == 'ATISW' or i == 'HL^B' or i =='LEN.B' or i == 'SAND          ':
                stock_symbol = stock_symbol.drop([idx])
        return stock_symbol

    def getNoneAmericanStockList(self):
        col = self.getColumnNames(self.stockdf)[0]  # return 'stock symbol'
        all_Stock_Symbol = self.stockdf[col]

        col_Mexico = self.getColumnNames(self.stockdf_Mexico)[0]  # return 'stock symbol'
        stock_symbol_Mexico = self.stockdf_Mexico[col_Mexico]
        col_Canada = self.getColumnNames(self.stockdf_Canada)[0]  # return 'stock symbol'
        stock_symbol_Canada = self.stockdf_Canada[col_Canada]
        col_NorthAmerican = self.getColumnNames(self.stockdf_NorthAmerican)[0]  # return 'stock symbol'
        stock_symbol_NorthAmerican = self.stockdf_NorthAmerican[col_NorthAmerican]

        for idx, i in enumerate(stock_symbol_NorthAmerican):
            if i in stock_symbol_Mexico or i in stock_symbol_Canada:
                stock_symbol_NorthAmerican = stock_symbol_NorthAmerican.drop([idx])
        print(len(stock_symbol_NorthAmerican))

        for idx_j, j in enumerate(all_Stock_Symbol):
            if j in list(stock_symbol_NorthAmerican) or j == 'ATISW' or j == 'HL^B' or j == 'LEN.B' or j == 'SAND          ':
                print(j)
                all_Stock_Symbol = all_Stock_Symbol.drop([idx_j])
        print(len(all_Stock_Symbol))
        none_USA_Symbol = all_Stock_Symbol
        return none_USA_Symbol


    def getColumnNames(self, stockdf):
        col_name_list = []
        for col in stockdf.columns:
            col_name_list += [col]
        return col_name_list

    def downloadDataToLocal(self):
        self.convertSymToJsonFile()
        self.saveMultiCompany()

    def saveStockDataToLocal(self, company):
        year, month, day = self.getCurrentDate()
        data = pdr.get_data_yahoo(company,
                                  start='{0}-{1}-{2}'.format(year-3, month, day),
                                  end='{0}-{1}-{2}'.format(year, month, day-1))

        dir_name = os.path.join(os.getcwd(), 'StockDataCSVFile')
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        file_name = '{}.csv'.format(company)
        path = os.path.join(dir_name, file_name)
        data.to_csv(path)

        c = self.stockDatabase.cursor()
        c.execute(
            'CREATE TABLE IF NOT EXISTS {}Data (Date_ REAL,High REAL,Low REAL,Open_price REAL,Close_price REAL,Volume REAL,Adj_close REAL)'.format(
                company))

        data.to_sql(company, self.stockDatabase, if_exists = 'replace')
        self.stockDatabase.commit()

    def getCurrentDate(self):
        currentDate = datetime.datetime.now()

        Year = currentDate.year
        Month = currentDate.month
        Day = currentDate.day
        return Year, Month, Day

    def saveMultiCompany(self):
        with open(self.stockSymbolJsonFile) as f:
            symbol_list = json.load(f)

        for key in symbol_list:
            company = symbol_list[key]
            self.saveStockDataToLocal(company)

    def accessCSV(self, company):
        dir_name = os.path.join(os.getcwd(), 'StockDataCSVFile')
        file_name = '{}.csv'.format(company)
        path = os.path.join(dir_name, file_name)
        dataCSV = pd.read_csv(path)
        header = list(dataCSV.columns)
        return dataCSV





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

        return True

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





