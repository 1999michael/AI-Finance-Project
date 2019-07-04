
import os
from Control.getStockData import getStockData


def main():
    getStockDataValue = getStockData()
    getStockDataValue.showStockData()
    a = getStockDataValue.getStockSymbol()
    getStockDataValue.convertSymToJsonFile(a)

if __name__ == "__main__":
    main()