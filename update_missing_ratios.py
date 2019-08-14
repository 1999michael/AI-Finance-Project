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
        
        # Missing Data From Parsing
        missing_data = []
        missing_data.append(["AES", "2018-05-08", "cash flow", 1780000000])
        missing_data.append(["AMRC", "2018-08-08", "cash flow", 4372000])
        missing_data.append(["AMRC", "2018-11-02", "cash flow", 36920000])
        missing_data.append(["AXTA", "2018-10-25", "cash flow", -171500000])
        missing_data.append(["CDE", "2018-04-25", "cash flow", -64231000])
        missing_data.append(["CDE", "2018-07-25", "cash flow", -36075000])
        missing_data.append(["CF", "2018-11-01", "cash flow", 187000000])
        missing_data.append(["CLF", "2019-04-25", "cash flow", -393000000])
        missing_data.append(["CMC", "2019-01-08", "cash flow", -575078000])
        missing_data.append(["CMC", "2019-03-26", "cash flow", -564452000])
        missing_data.append(["CMC", "2019-06-27", "cash flow", -510306000])
        missing_data.append(["FMC", "2019-05-08", "cash flow", -52200000])
        missing_data.append(["GRA", "2019-02-28", "cash flow", 37500000])
        missing_data.append(["HL", "2018-11-09", "cash flow", -125273000])
        missing_data.append(["IFF", "2019-05-06", "cash flow", -151393000])
        missing_data.append(["IP", "2018-08-03", "cash flow", 55000000])
        missing_data.append(["IP", "2018-11-02", "cash flow", 8000000])
        missing_data.append(["LEN", "2016-01-22", "return on equity", -0.004485491])
        missing_data.append(["LEN", "2016-01-22", "working capital", -7310992000])
        missing_data.append(["LEN", "2016-04-06", "working capital", -4613522000])
        missing_data.append(["LEN", "2016-07-01", "working capital", -14032324000])
        missing_data.append(["LEN", "2016-10-04", "working capital", -7419719000])
        missing_data.append(["LEN", "2017-01-20", "return on equity", -0.019880343])
        missing_data.append(["LEN", "2017-01-20", "working capital", -6820685000])
        missing_data.append(["LEN", "2017-04-10", "working capital", -8045278000])
        missing_data.append(["LEN", "2017-06-30", "working capital", -8333531000])
        missing_data.append(["LEN", "2017-10-10", "working capital", -8442187000])
        missing_data.append(["LEN", "2018-01-25", "return on equity", -0.001541046])
        missing_data.append(["LEN", "2018-01-25", "working capital", -8108030000])
        missing_data.append(["LEN", "2018-04-09", "working capital", -13740354000])
        missing_data.append(["LEN", "2018-07-06", "working capital", -13498385000])
        missing_data.append(["LEN", "2018-10-09", "working capital", -13124799000])
        missing_data.append(["LEN", "2019-01-28", "working capital", -12324766000])
        missing_data.append(["LEN", "2019-04-08", "working capital", -13639473000])
        missing_data.append(["LEN", "2019-07-03", "working capital", -14097967000])   
        missing_data.append(["LEU", "2018-05-10", "cash flow", -55300000])
        missing_data.append(["LEU", "2018-08-09", "cash flow", -68500000])
        missing_data.append(["LEU", "2018-11-08", "cash flow", -83500000])
        missing_data.append(["LEU", "2019-04-01", "cash flow", -85100000])
        missing_data.append(["LEU", "2019-05-09", "cash flow", -35000000])
        missing_data.append(["MAS", "2016-02-12", "cash flow", 85000000])
        missing_data.append(["MAS", "2017-02-09", "cash flow", -478000000])
        missing_data.append(["MAS", "2018-02-08", "cash flow", 204000000])
        missing_data.append(["MAS", "2019-02-07", "cash flow", -635000000])
        missing_data.append(["MOS", "2018-08-07", "cash flow", 40200000])
        missing_data.append(["MOS", "2018-11-06", "cash flow", 20100000])
        missing_data.append(["NG", "2016-04-04", "return on equity", -0.044219453])
        missing_data.append(["NG", "2016-06-27", "return on equity", 0.003513637])
        missing_data.append(["NG", "2016-10-04", "return on equity", -0.02333])
        missing_data.append(["NG", "2017-01-25", "return on equity", -0.10892])
        missing_data.append(["NG", "2017-04-03", "return on equity", -0.020531])
        missing_data.append(["NG", "2018-01-24", "return on equity", -0.08170])
        missing_data.append(["NG", "2018-04-04", "return on equity", -0.019984])
        missing_data.append(["NG", "2018-06-27", "return on equity", -0.048424824])
        missing_data.append(["NG", "2019-01-23", "return on equity", -0.815667629])
        missing_data.append(["NG", "2019-04-02", "return on equity", -0.01944])
        missing_data.append(["NG", "2019-06-26", "return on equity", -0.01694])
        missing_data.append(["OLN", "2017-08-01", "cash flow", 1])
        missing_data.append(["OMN", "2016-04-06", "cash flow", -1400000])
        missing_data.append(["OMN", "2016-06-29", "cash flow", 15700000])
        missing_data.append(["OMN", "2016-09-22", "cash flow", 25400000])
        missing_data.append(["OMN", "2017-03-29", "cash flow", -7600000])
        missing_data.append(["OMN", "2017-06-28", "cash flow", -3400000])
        missing_data.append(["OMN", "2017-09-28", "cash flow", 2600000])
        missing_data.append(["OMN", "2018-03-28", "cash flow", -51900000])
        missing_data.append(["PG", "2016-01-26", "cash flow", 2567000000])
        missing_data.append(["PZG", "2019-05-10", "cash flow", 64588])
        missing_data.append(["REGI", "2017-03-10", "cash flow", 69712000])
        missing_data.append(["REGI", "2018-03-09", "cash flow", -40213000])
        missing_data.append(["SRCL", "2018-11-01", "cash flow", 9800000])
        missing_data.append(["TMQ", "2016-02-08", "return on equity", -0.189014475])
        missing_data.append(["TMQ", "2016-04-07", "return on equity", -0.03460031])
        missing_data.append(["TMQ", "2016-07-07", "return on equity", -0.034726904])
        missing_data.append(["TMQ", "2016-10-06", "return on equity", -0.098159084])
        missing_data.append(["TMQ", "2017-02-03", "return on equity", -0.0105342982])
        missing_data.append(["TMQ", "2017-04-04", "return on equity", -0.068932195])
        missing_data.append(["TMQ", "2017-06-28", "return on equity", -0.05804352])
        missing_data.append(["TMQ", "2017-10-05", "return on equity", -0.278484932])
        missing_data.append(["TMQ", "2018-02-02", "return on equity", -0.822287161])
        missing_data.append(["TMQ", "2018-04-05", "return on equity", -0.124614018]) 
        missing_data.append(["TMQ", "2018-07-16", "return on equity", -0.077859708])
        missing_data.append(["TMQ", "2018-07-16", "cash flow", 32067000])
        missing_data.append(["TMQ", "2018-10-05", "return on equity", -0.265545948])
        missing_data.append(["TMQ", "2018-10-05", "cash flow", 25078000])
        missing_data.append(["TMQ", "2019-02-11", "return on equity", -0.678498229])
        missing_data.append(["TMQ", "2019-04-09", "return on equity", -0.145478946])
        missing_data.append(["TMQ", "2019-07-09", "return on equity", -0.173690292])
        missing_data.append(["UEC", "2019-03-12", "cash flow", -2921570])
        missing_data.append(["UEC", "2019-06-10", "cash flow", -410481])
        missing_data.append(["VGZ", "2018-10-29", "cash flow", -360000])
        
        # If we ever choose to do anything with these
        missing_data_skip = []
        missing_data_skip.append(["UEC", "2016-03-11", "asset turnover"])
        missing_data_skip.append(["UEC", "2016-06-09", "asset turnover"])
        missing_data_skip.append(["UEC", "2016-10-14", "asset turnover"])
        missing_data_skip.append(["UEC", "2016-12-12", "asset turnover"])
        missing_data_skip.append(["UEC", "2017-03-13", "asset turnover"])
        missing_data_skip.append(["UEC", "2017-06-09", "asset turnover"])
        missing_data_skip.append(["UEC", "2017-10-16", "asset turnover"])    
        missing_data_skip.append(["VGZ", "2016-02-26", "asset turnover"])
        missing_data_skip.append(["VGZ", "2016-04-29", "asset turnover"])
        missing_data_skip.append(["VGZ", "2016-08-01", "asset turnover"])
        missing_data_skip.append(["VGZ", "2016-10-26", "asset turnover"])
        missing_data_skip.append(["VGZ", "2017-02-22", "asset turnover"])
        missing_data_skip.append(["VGZ", "2017-04-28", "asset turnover"])
        missing_data_skip.append(["VGZ", "2017-08-04", "asset turnover"])
        missing_data_skip.append(["VGZ", "2017-10-25", "asset turnover"])
        missing_data_skip.append(["VGZ", "2018-03-06", "asset turnover"])
        missing_data_skip.append(["VGZ", "2018-04-27", "asset turnover"])
        missing_data_skip.append(["VGZ", "2018-07-25", "asset turnover"])
        missing_data_skip.append(["VGZ", "2019-02-25", "asset turnover"])
        missing_data_skip.append(["VGZ", "2019-05-07", "asset turnover"])   
        print("num of skipped data points: " + str(len(missing_data_skip)))
        
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
                for missing_data_point in missing_single_point_list:
                        if (missing_data_point[0] == ratio['symbol'] and missing_data_point[1] == ratio['date']):
                                ratio['PPS'] = missing_data_point[2]
        
        for ratio in data:
                for missing_data_point in missing_data:
                        if (missing_data_point[0] == ratio['symbol'] and missing_data_point[1] == ratio['date']):
                                ratio[missing_data_point[2]] = missing_data_point[3]
        
        return data

def check(data):
        symbol_count = 0
        symbol = data[0]["symbol"]
        counter = [0,0,0,0]
        zeros = 0
        ratios = ["current ratio", "PPS", "EPS", "asset turnover", "PE ratio", "cash flow", "return on equity", "working capital"]

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
        
        zero_points_str = []

        # Check number of zero data points
        count = 0
        for item in data:
                for ratio in ratios:
                        if (item[ratio] == float(0)):
                                zeros += 1
        # Print results
        print("num companies with 13 financial statements:           " + str(counter[0]))
        print("num companies with 14 financial statements:           " + str(counter[1]))
        print("num companies with 15 financial statements:           " + str(counter[2]))
        print("num companies with other num of financial statements: " + str(counter[3]))
        print("num companies :                                       " + str(counter[0] + counter[1] + counter[2] + counter[3]))
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
                if (data[item_num]["PE ratio"] == float(0)):
                        try:
                                data[item_num]["PE ratio"] = data[item_num]["PPS"] / data[item_num]["EPS"]
                        except:
                                print(data[item_num]["symbol"], data[item_num]["date"])
        check(data)
        write_ratios(data)

update_pps_and_pe_ratio()
