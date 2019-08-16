# AI-Finance-Project

*data_txt folder contains all .txt and .json files*

data_list_complete.json has all the ratios and stock price data we will/may use (contains 22 data features per day, per company, but we only use the first 14 of the 22 as through testing, we found the first 14 features to be as good as using all 22 features).

add_new_ratios.py allows us to add new ratios / indicators to our data_list_complete.json file

baseline_model.ipynb contains 2 baseline models and the best model architecture

NOTE 1: Running Financial_Statement_Parsing *WILL NOT* recreate the same file as manual input was necessary for the completion of the data_numbers.txt file, which generated the data_ratios.txt file, but generates a good portion of the ratios

NOTE 2: The companies that are to be neglected due to missing net sales or assets/liabilities are 
"LEN", "GMO", "NG", "TMQ", "UEC", "VGZ", "WWR", "XPL"
