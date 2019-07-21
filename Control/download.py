import os
from getStockData import getStockData


def download():
    getStockDataValue = getStockData()
    #getStockDataValue.convertSymToJsonFile()
    getStockDataValue.downloadDataToLocal()
    #getStockDataValue.getstockprice('2016-11-18', 'KL')
    getStockDataValue.MultiCompanyPrice()
if __name__ == "__main__":
    download()