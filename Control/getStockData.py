import pandas as pd
import os

class getStockData:
    def __init__(self):
        self.stockdf = pd.read_csv(
            "https://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Basic+Industries&render=download",
            index_col=False)

    def getColumnNames(self):
        col_name_list = []
        for col in self.stockdf.columns:
            col_name_list += [col]
        return col_name_list

    def getStockSymbol(self):
        col = self.getColumnNames()[0]
        stock_symbol = self.stockdf[col]
        print(type(stock_symbol))
        print(stock_symbol.shape)
        return stock_symbol

    def convertSymToJsonFile(self,symbol_list):
        cur_dir = os.getcwd()
        name = 'Stock_Symbols_CSV.json'
        json_path = os.path.join(cur_dir,name)
        a = symbol_list.to_json(json_path)
        print(type(a))

    def showStockData(self):

        return self.stockdf







