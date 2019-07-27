import ast
import os
import json
from collections import OrderedDict

def write_ratios(all_data):
        f = open( 'data_ratios.txt', 'w' )             # Use .txt file for now
        for i in all_data:
                f.write(str(i) + "\n")
        f.close()
        return True

def read_ratios():                       # Take in raw .txt file, and convert to dictionary
        with open("data_ratios.txt") as f:
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary
        return data
    
def get_pps(symbol, date):
        wrk_directory = os.getcwd()
        for dirpath, dirnames, files in os.walk('Price_Json_File'):
                with open(wrk_directory + '/' + dirpath + "/price_" + symbol + ".json") as json_file:
                        data = json.load(json_file)
        
        price = data[date]
        return price

def insert_manual(data):
        # Companies to remove due to insufficient data
        missing_companies_list = []
        missing_companies_list.append("VMC")
        missing_companies_list.append("WLKP")
        missing_companies_list.append("VRS")

        # Datapoints that had their financial statement release on a day the market wasn't open
        missing_single_point_list = []
        missing_single_point_list.append(["MSB", "2017-04-14", 15.020000457763672])
        missing_single_point_list.append(["PPG", "2019-04-19", 119.86000061035156])
        missing_single_point_list.append(["REX", "2016-03-25", 53.54999923706055])
        missing_single_point_list.append(["SKY", "2017-04-14", 8.449999809265137])

        index_to_remove = []
        count = 0
        for ratio in data:
                if (ratio["symbol"] in missing_companies_list):
                        index_to_remove.append(count)
                count += 1

        index_to_remove.reverse()

        for i in index_to_remove:
                del data[i]
                
        for ratio in data:
                for missing_data in missing_single_point_list:
                        if (missing_data[0] == ratio['symbol'] and missing_data[1] == ratio['date']):
                                ratio['PPS'] = missing_data[2]
        return data

def check(data):
        symbol_count = 0
        symbol = data[0]["symbol"]
        counter = [0,0,0,0]
        zeros = 0

        # Check number of quarterly reports per company 
        for item in data:
                if (item["symbol"] == symbol):
                        symbol_count += 1
                else:
                        if (symbol_count == 13):
                                counter[0] += 1
                        elif (symbol_count == 14):
                                counter[1] += 1
                        elif (symbol_count == 15):
                                counter[2] += 1
                        else:
                                counter[3] += 1
                        symbol_count = 1
                        symbol = item["symbol"]

        # Check number of zero data points
        for item in data:
                for data in item:
                        if (type(data) != str):
                                if (float(data) == 0.0):
                                        zeros += 1
        
        # Print results
        print("num companies with 13 financial statements:           " + str(counter[0]))
        print("num companies with 14 financial statements:           " + str(counter[1]))
        print("num companies with 15 financial statements:           " + str(counter[2]))
        print("num companies with other num of financial statements: " + str(counter[3]))
        print("num of zero data points:                              " + str(zeros))
        return True

def update_pps_and_pe_ratio():
        data = read_ratios()
        data = insert_manual(data)

        # UPDATING PPS
        for item_num in range(len(data)):
                if (data[item_num]["PPS"] == 0):
                        try:
                                data[item_num]["PPS"] = get_pps(data[item_num]["symbol"], data[item_num]["date"])
                        except:
                                print(data[item_num]["symbol"], data[item_num]["date"])

        # UPDATING PE RATIOS
        for item_num in range(len(data)):
                if (data[item_num]["PPS"] == 0.0):
                        try:
                                data[item_num]["PPS"] = get_pps(data[item_num]["symbol"], data[item_num]["date"])
                        except:
                                print(data[item_num]["symbol"], data[item_num]["date"])
        check(data)
        write_ratios(data)

update_pps_and_pe_ratio()