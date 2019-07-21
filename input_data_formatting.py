import json
import ast
import datetime  
from datetime import timedelta 

def read_from_database_ratios():                            # Take in raw .txt file, and convert to dictionary
    with open("data_ratios.txt") as f:
            content = f.readlines()
    content = [x.strip() for x in content] 
    data = []
    for i in range(0,len(content)):
            data.append(ast.literal_eval(content[i]))       # Converting to dictionary
    return data

def get_price(symbol, date):
    file = "Price_Json_File\price_" + symbol + ".json"
    with open(file) as json_file:  
        data = json.load(json_file)
    price = data[date]
    return price

ratios = read_from_database_ratios()

closing_price = get_price("AIN", "2016-02-26")
print(closing_price)
