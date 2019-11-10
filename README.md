# AI-Finance-Project
Stock Price Direction Prediction

The goal of this project is to make a predict the stock price direction of the closing stock of 160 stocks in the American basics material industry for the companies that have went public from 2015 November 11th or before.

Extracting report branch --> Data downloading files

All_Company_LSTM_Model --> Contains the all-companies LSTM model

Generic-Approach-LSTM/GRU --> Contains the generic LSTM final model (also having tested GRU as an option)

FINAL TEST ACCURACY: 82.1%

data_list_complete.json complete file data variables:
    Financial Statement Ratios
        0 = EPS
        1 = PE ratio
        2 = PPS
        3 = asset turnover
        4 = cash flow
        5 = current ratio
        6 = return on equity
        7 = working capital
    Stock Prices and Indicators
        8 = Closing stock price       **MUST BE PRESENT TO MAKE LABELS**
        9 = 14-day moving avg
        10 = 37-day moving average
        11 = 14-day stochastic moving oscillator
        12 = 3-day stochastic moving average
        13 = relative strength index
        14 = 14 day stochastic oscillator
        15 = 3 day stochastic moving average
        16 = 14 day relative strength index
        17 = Open price
        18 = 12 day exponential moving average
        19 = 26 day exponential moving average
        20 = moving average convergence divergence
        21 = 25 day moving average
        22 = 50 day moving average
