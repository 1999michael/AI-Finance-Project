# AI-Finance-Project
Stock Price Direction Prediction

The goal of this project is to make a predict the stock price direction of the closing stock of 160 stocks in the American basics material industry for the companies that have went public from 2015 November 11th or before.

Extracting report branch --> Data downloading files

All_Company_LSTM_Model --> Contains the all-companies LSTM model

Generic-Approach-LSTM/GRU --> Contains the generic LSTM final model (also having tested GRU as an option)

FINAL TEST ACCURACY: 82.1%

---
Data Documentation

Currently we can use up to 23 variables extracted from both financial statements and stock prices and stock indicators. Below are the variable with their corresponding index within data_list_complete.json.  
Financial Statement Ratios  
<ul>
    <li>0 = EPS  </li>
    <li>1 = PE ratio  </li>
    <li>2 = PPS  </li>
    <li>3 = asset turnover  </li>
    <li>4 = cash flow  </li>
    <li>5 = current ratio  </li>
    <li>6 = return on equity  </li> 
    <li>7 = working capital  </li>
</ul>
Stock Prices and Indicators  

<ul>
    <li>8 = Closing stock price       **MUST BE PRESENT TO MAKE LABELS** </li> 
    <li>9 = 14-day moving avg  </li>
    <li>10 = 37-day moving average  </li>
    <li>11 = 14-day stochastic moving oscillator  </li>
    <li>12 = 3-day stochastic moving average  </li>
    <li>13 = relative strength index  </li>
    <li>14 = 14 day stochastic oscillator  </li>
    <li>15 = 3 day stochastic moving average  </li>
    <li>16 = 14 day relative strength index  </li>
    <li>17 = Open price  </li>
    <li>18 = 12 day exponential moving average  </li>
    <li>19 = 26 day exponential moving average  </li>
    <li>20 = moving average convergence divergence  </li>
    <li>21 = 25 day moving average  </li>
    <li>22 = 50 day moving average  </li>
</ul>
