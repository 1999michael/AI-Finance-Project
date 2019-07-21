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


        for idx_j, j in enumerate(all_Stock_Symbol):
            if j in list(stock_symbol_NorthAmerican) or j == 'ATISW' or j == 'HL^B' or j == 'LEN.B' or j == 'SAND          ':
                all_Stock_Symbol = all_Stock_Symbol.drop([idx_j])

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
        file_name = '{}_Data.csv'.format(company)
        path = os.path.join(dir_name, file_name)
        data.to_csv(path)

        #c = self.stockDatabase.cursor()
        #c.execute('CREATE TABLE IF NOT EXISTS {}_AllData (Date_ REAL,High REAL,Low REAL,Open_price REAL,Close_price REAL,Volume REAL,Adj_close REAL)'.format(company))

        data.to_sql('{}_AllData'.format(company), self.stockDatabase, if_exists = 'replace')
        #self.stockDatabase.commit()

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
        file_name = '{}_Data.csv'.format(company)
        path = os.path.join(dir_name, file_name)
        dataCSV = pd.read_csv(path)
        header = list(dataCSV.columns)
        return dataCSV

    def getCompanyStock(self, company):
        c = self.stockDatabase.cursor()
        c.execute("SELECT ({col_name}) FROM {table}_AllData".format(col_name='Close', table=company))
        all_price = c.fetchall()
        c.execute("SELECT ({col_name}) FROM {table}_AllData".format(col_name='Date', table=company))
        all_date = c.fetchall()
        price_list = []

        for i, price_row in enumerate(all_price):
            price_list = price_list + [price_row[0]]

        company_stock_dict = {}
        for i, date_row in enumerate(all_date):
            company_stock_dict[date_row[0][0:10]] = price_list[i]

        dir_name = os.path.join(os.getcwd(), 'Price_Json_File')
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)


        price_json = 'price_{}.json'.format(company)

        json_path = os.path.join(dir_name, price_json)
        json.dump(company_stock_dict, open(json_path, 'w'))

    def MultiCompanyPrice(self):
        cur_dir = os.getcwd()
        name = 'Stock_Symbols.json'

        json_path = os.path.join(cur_dir, name)
        self.stockSymbolJsonFile = json_path
        with open(self.stockSymbolJsonFile) as f:
            symbol_list = json.load(f)

        for key in symbol_list:
            company = symbol_list[key]
            self.getCompanyStock(company)
        return True