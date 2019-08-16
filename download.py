import os
from Control.getStockData import getStockData


def download():
    getStockDataValue = getStockData()
    getStockDataValue.convertSymToJsonFile()
    getStockDataValue.downloadDataToLocal()
    getStockDataValue.MultiCompanyPrice()

if __name__ == "__main__":
    download()
