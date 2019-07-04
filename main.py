
import os
from Control.getStockData import getStockData


def main():
    getStockDataValue = getStockData()
    getStockDataValue.showStockData()
    a = getStockDataValue.getStockSymbol()
    getStockDataValue.convertSymToJsonFile(a)

# if name == "main":
#  slideManager = SlideManager()
#  slideManager.baseDirectory = "/Users/kailin/Desktop/base_dir"

#  slideManager.addSlide(1)
#  slide1 = slideManager.getSlide(1)

#  image = Image("/Users/kailin/Desktop/tmp/1006/IAPS_N_7043.jpg")
#  slide1.addImage(image)


if __name__ == "__main__":
    main()