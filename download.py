import os
from Control.getStockData import getStockData


def download():
    getStockDataValue = getStockData()
    getStockDataValue.convertSymToJsonFile()
    getStockDataValue.downloadDataToLocal()
if __name__ == "__main__":
    download()