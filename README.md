# AI-Finance-Project
Stock Price Direction Prediction

This is the branch including some data collecting on historical stock data and processing file. Note, in order to run the data code, first ensure you have the following installed with updated python, so no Python 2.7
pip install sql
pip install pandas
pip install pandas-datareader

getStockData.py is used for extracting data from online sources, it is used to support download.py running. 

InputManager.py is used for assisting the action of combining financial statement data and historical stock price into one same file.InputManager.py is used to support the running of dataProcess.py. 

To perform data collecting on the historical stock data, simply download whatever is in the github then do:
python download.py 

The data_list_complete.json includes all the data that will be used for reformatting and input to the model. To obtain data_list_complete.json for creating input, you can either obtain from the branch or run following code after python download.py: 
python dataProcess.py

The code and the training result for the All Companies model can be found in the LSTM_V2.ipynb file. 


