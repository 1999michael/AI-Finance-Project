import ast
import os
import json
import shutil
from collections import OrderedDict
import csv

# ==========================================
# ======= Read and Write to Database =======
# ==========================================

def read_ratios():                       # Take in raw .txt file, and convert to dictionary
        with open("data_ratios.txt") as f:
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary
        return data

def to_database(all_data):
        f = open( 'data_list_complete.json', 'w' )             # Use .txt file for now
        #for i in all_data:
        f.write(str(all_data))
        f.close()
        return True

# =======================================================
# ======= Cleaning Bad Data (companies and files) =======
# =======================================================

def remove_bad_data():
        data = read_ratios()
        company_list = []
        for i in data:
                if (i["symbol"] not in company_list):
                        company_list.append(i["symbol"])
        remove_bad_files(company_list)
        return True

def remove_bad_files(company_list):                 # Remove all company symbol folders with less than 14 financial statements and Non-american
        wrk_directory = os.getcwd()
        for dirpath, dirnames, files in os.walk('.\StockDataCSVFile'):
                symbols = []
                for i in range(len(files)):
                        symbols.append(files[i].split(".")[0].split("_")[0])
                for i in range(len(files)):
                        if (symbols[i] not in company_list):
                                old_directory = wrk_directory + dirpath[1:] + "\\" + files[i]     # Bad file source
                                new_directory = wrk_directory + "\\ObsoleteStockDataCSVFiles"     # Bad file destination
                                shutil.move(old_directory, new_directory)               # Move bad symbols to obsolete folder
        return True

# ============================================
# ======= Read a single company's data =======
# ============================================

def read_file(symbol):
        with open("StockDataCSVFile\\" + symbol + "_DATA.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                values = [] # Date, High, Low, Open, Close
                start = True
                for row in csv_reader:
                        if (start):
                                start = False
                        else:
                                values.append([row[0], float(row[1]), float(row[2]), float(row[3]), float(row[4])])
        return values        

# ===========================================
# ======= Read and Add New Datapoints =======
# ===========================================

def read_from_database_to_list(data_points = range(0,20), filename = "data_list_complete.json"):      # Take in raw str, and convert to dictionary, then to list

        with open(filename, "r") as f:              # *******FILE LOCATION/NAME MAY DIFFER ACCORDING TO YOUR REQUIREMENTS******
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary

        data = data[0]
        list_companies = list(data["2019-07-17"].keys())        # All company symbols (anyday works after april 14th 2019)
        list_companies.sort(reverse = False)                    # Sort alphabetically company names

        list_days = list(data.keys())                           # All database days
        list_days = sorted(list_days, key = sorting)            # Sort days in past -> future order
                
        bad_companies = ["WLKP", "VMC", "VRS", "REX", "USLM"]   # These companies data are incomplete. To be removed (not enough data) --> I ADDED "USLM" TO MAKE IT WORK ???
        bad_days = []                                           # List of incomplete days (mostly comprised of days before april 14th 2019)

        for day in list_days:                                   # Delete bad days and companies
                num_companies = len(data[day])
                for company in list_companies:
                        if (company in bad_companies and company in data[day]):
                                del data[day][company]
                        if (num_companies < 160):
                                del data[day]
                                bad_days.append(day)
                                break

        for company in bad_companies:                           # Remove bad companies from company list
                if(company in list_companies):
                        list_companies.remove(company)

        for day in bad_days:                                    # Remove bad days from days list
                list_days.remove(day)
                
        # ADD NEW NUMBERS HERE
        for company in list_companies:
                data_indv_company = data_collect(company, list_days)
                for day in list_days:
                        data[day][company] += data_indv_company[day]
        
        to_database(data)
        
        check_file(len(data_points))
        
        return data            # Type list with all requested data

def sorting(L):                     # Function to sort the days in chronological order
        splitup = L.split('-')
        return splitup[0], splitup[1], splitup[2]

def check_file(new_num_data_points):
        with open("data_list_complete.json", "r") as f:              # *******FILE LOCATION/NAME MAY DIFFER ACCORDING TO YOUR REQUIREMENTS******
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary
        
        data = data[0]
        list_companies = list(data["2019-07-17"].keys())        # All company symbols (anyday works after april 14th 2019)
        list_companies.sort(reverse = False)                    # Sort alphabetically company names
        
        list_days = list(data.keys())                           # All database days
        list_days = sorted(list_days, key = sorting)            # Sort days in past -> future order
                
        bad_companies = ["WLKP", "VMC", "VRS", "REX", "USLM"]   # These companies data are incomplete. To be removed (not enough data) --> I ADDED "USLM" TO MAKE IT WORK ???
        bad_days = []                                           # List of incomplete days (mostly comprised of days before april 14th 2019)
        
        for day in list_days:                                   # Delete bad days and companies
                num_companies = len(data[day])
                for company in list_companies:
                        if (company in bad_companies and company in data[day]):
                                del data[day][company]
                        if (num_companies < 160):
                                del data[day]
                                bad_days.append(day)
                                break
        
        for company in bad_companies:                           # Remove bad companies from company list
                if(company in list_companies):
                        list_companies.remove(company)
        
        for day in bad_days:                                    # Remove bad days from days list
                list_days.remove(day)
                
        data_points = range(0, new_num_data_points)
        num_days = len(data)                                    # Dimensions of data
        num_companies = len(data["2016-04-15"])
        num_data_points = len(data_points)
        
        list_data = [[[0 for i in range(num_data_points)] for j in range(num_companies)] for k in range(num_days)]
        
        # Input all data to premade 3D list in order    
        counter_i = 0
        counter_j = 0
        counter_k = 0
        
        for day in list_days:
                for company in list_companies:
                        for data_point in data_points:
                                list_data[counter_i][counter_j][counter_k] = data[day][company][data_point]
                                counter_k += 1
                        counter_k = 0
                        counter_j += 1
                counter_j = 0
                counter_i += 1
        
        count_correct = 0
        count_incorrect = 0
        for i in list_data:
                for j in i:
                        if (len(j) == num_data_points):
                                count_correct += 1
                        else:
                                count_incorrect += 1
        
        print(str(num_data_points) + " count", count_correct)
        print("Other count", count_incorrect)
        return True
# ====================================================================================================
# ============================== ONLY ADJUST CODE BELOW THIS LINE ====================================
# ====================================================================================================

# =========================================
# ======= Stock Indicator Functions =======
# =========================================

def stochastic_oscillator_14_day(symbol, start_date):   # %k = (current close - lowest low) / (highest high - lowest low) --> Over 14 days
        values = read_file(symbol) # Get CSV data
        SO_14_days = []
        start_index = 0 # Get start date index    
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
                        
        for i in range(start_index, len(values)):
                SO = 0.0
                low = values[i][2]
                high = values[i][1]
                for j in range(i - 13, i + 1):
                        if (values[j][2] < low):
                                low = values[j][2]
                        if (values[j][1] > high):
                                high = values[j][1]
                SO = (values[i][4] - low) / (high - low) 
                SO_14_days.append([values[i][0], SO])
        SO_14_days_dict = {}
        for i in range(len(SO_14_days)):
                SO_14_days_dict[SO_14_days[i][0]] = SO_14_days[i][1]
        return SO_14_days_dict

def stochastic_moving_average_3_day(symbol, start_date):   # %D = moving average over 3 days of 14-day stochastic indicator
        values = read_file(symbol) # Get CSV data
        SMA_3_day = []
        start_index = 0 # Get start date index    
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
                        
        for i in range(start_index, len(values)):
                SMA = 0.0
                for j in range(0,3):
                        low = values[i-j-13][2]
                        high = values[i-j-13][1]
                        for k in range(i - 13 - j, i + 1 - j):
                                if (values[k][2] < low):
                                        low = values[k][2]
                                if (values[k][1] > high):
                                        high = values[k][1]
                        SMA += (values[i-j][4] - low) / (high - low) 
                SMA_3_day.append([values[i][0], SMA/3.0])
        SMA_3_day_dict = {}
        for i in range(len(SMA_3_day)):
                SMA_3_day_dict[SMA_3_day[i][0]] = SMA_3_day[i][1]
        return SMA_3_day_dict

def relative_strength_index_14_day(symbol, start_date):
        values = read_file(symbol) # Get CSV data
        RSI_14_day = []
        start_index = 0 # Get start date index    
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
                        
        for i in range(start_index, len(values)):
                RSI = 0.0
                loss = 0.0
                loss_count = 0.0
                gain = 0.0
                gain_count = 0.0
                ref = values[i][4]
                for j in range(i - 13 , i + 1):
                        if (values[j][4] < ref):
                                loss += values[j][4] 
                                loss_count += 1.0
                        if (values[j][4] > ref):
                                gain += values[j][4] / ref
                                gain_count += 1.0
                                
                if (loss_count == 0.0):
                        RSI_14_day.append([values[i][0], 1.0])
                        continue
                elif (gain_count == 0.0):
                        RSI_14_day.append([values[i][0], 0.0])
                        continue
                        
                loss = loss / loss_count
                gain = gain / gain_count
                
                RSI = (100.0 - (100.0 / (1.0 + (gain/loss)))) / 100.0
                
                RSI_14_day.append([values[i][0], RSI])     
        
        RSI_14_day_dict = {}
        for i in range(len(RSI_14_day)):
                RSI_14_day_dict[RSI_14_day[i][0]] = RSI_14_day[i][1]                
        return RSI_14_day_dict

def open_price(symbol, start_date):   # %k = (current close - lowest low) / (highest high - lowest low) --> Over 14 days
        values = read_file(symbol) # Get CSV data
        start_index = 0 # Get start date index    
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        open_dict = {}                
        for i in range(start_index, len(values)):
                open_dict[values[i][0]] = values[i][3]
        return open_dict

def EMA_12(symbol, start_date):
        values = read_file(symbol)
        ema_12 = {}
        start_index = 0
        SMA = 0.0
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        
        for i in range(start_index - 12, start_index):
                SMA += values[i][2]
                
        ema_12[values[start_index][0]] = SMA / 12.0
        
        for i in range(start_index + 1, len(values)):
                for j in range(i - 12, i):
                        ema_12[values[i][0]] = (values[i][2]*(2/(12+1))) + (ema_12[values[i-1][0]] * (1 - (2/(12+1))))
        return ema_12

def EMA_26(symbol, start_date):
        values = read_file(symbol)
        ema_26 = {}
        start_index = 0
        SMA = 0.0
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        
        for i in range(start_index - 26, start_index):
                SMA += values[i][2]
                
        ema_26[values[start_index][0]] = SMA / 26.0
        
        for i in range(start_index + 1, len(values)):
                for j in range(i - 26, i):
                        ema_26[values[i][0]] = (values[i][2]*(2/(26+1))) + (ema_26[values[i-1][0]] * (1 - (2/(26+1))))
        return ema_26
                        
def moving_avg_conv_div(symbol, start_date):
        values = read_file(symbol)
        moving_avg_conv_div = {}
        start_index = 0
        SMA_12 = 0.0
        SMA_26 = 0.0
        ema_26_curr = 0.0
        ema_26_prev = 0.0
        ema_12_curr = 0.0
        ema_12_prev = 0.0
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        
        for i in range(start_index - 26, start_index):
                SMA_26 += values[i][2]
                
        for i in range(start_index - 12, start_index):
                SMA_12 += values[i][2]
                
        ema_26_prev = SMA_26 / 26.0
        ema_12_prev = SMA_12 / 12.0
        moving_avg_conv_div[values[start_index][0]] = ema_26_prev - ema_12_prev
        
        for i in range(start_index + 1, len(values)):
                for j in range(i - 26, i):
                        ema_26_curr = (values[i][2]*(2/(26+1))) + (ema_26_prev * (1 - (2/(26+1))))
                        ema_26_prev = ema_26_curr
                for j in range(i - 12, i):
                        ema_12_curr = (values[i][2]*(2/(12+1))) + (ema_12_prev * (1 - (2/(12+1))))
                        ema_12_prev = ema_12_curr
                moving_avg_conv_div[values[i][0]] = ema_26_curr - ema_12_curr
        return moving_avg_conv_div

def moving_avg_25_day(symbol, start_date):
        values = read_file(symbol)
        moving_avg_25_day = {}
        start_index = 0
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        
        for i in range(start_index, len(values)):
                moving_avg = 0.0
                for j in range(i - 25, i):
                        moving_avg += values[i][2]
                moving_avg_25_day[values[i][0]] = moving_avg / 25.0
        return moving_avg_25_day

def moving_avg_50_day(symbol, start_date):
        values = read_file(symbol)
        moving_avg_50_day = {}
        start_index = 0
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        
        for i in range(start_index, len(values)):
                moving_avg = 0.0
                for j in range(i - 50, i):
                        moving_avg += values[i][2]
                moving_avg_50_day[values[i][0]] = moving_avg / 50.0
        return moving_avg_50_day

def high_price(symbol, start_date):
        values = read_file(symbol) # Get CSV data
        start_index = 0 # Get start date index    
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        high_dict = {}                
        for i in range(start_index, len(values)):
                high_dict[values[i][0]] = values[i][1]
        return high_dict

def low_price(symbol, start_date):
        values = read_file(symbol) # Get CSV data
        start_index = 0 # Get start date index    
        
        for i in values:
                if(i[0] == start_date):
                        break
                else:
                        start_index += 1
        low_dict = {}                
        for i in range(start_index, len(values)):
                low_dict[values[i][0]] = values[i][2]
        return low_dict

# =================================================
# ========== New Data Function Collector ==========
# =================================================

def data_collect(company, list_days, start_date = "2016-04-15"):
        all_new_data = {}

        #SO_14_day = stochastic_oscillator_14_day(company, start_date)
        #SMA_3_day = stochastic_moving_average_3_day(company, start_date)
        #RSI_14_day = relative_strength_index_14_day(company, start_date)
        #open_price_value = open_price(company, start_date)
        #ema_12 = EMA_12(company, start_date)
        #ema_26 = EMA_26(company, start_date)
        #macd = moving_avg_conv_div(company, start_date)
        #ma_25_day = moving_avg_25_day(company, start_date)
        #ma_50_day = moving_avg_50_day(company, start_date)
        high_prices = high_price(company, start_date)
        low_prices = low_price(company, start_date)        
        
        for day in list_days:
                indv_data_list = []
                #indv_data_list += [SO_14_day[day]]
                #indv_data_list += [SMA_3_day[day]]
                #indv_data_list += [RSI_14_day[day]]
                #indv_data_list += [open_price_value[day]]
                #indv_data_list += [ema_12[day]]
                #indv_data_list += [ema_26[day]]
                #indv_data_list += [macd[day]]
                #indv_data_list += [ma_25_day[day]]
                #indv_data_list += [ma_50_day[day]]
                indv_data_list += [high_prices[day]]
                indv_data_list += [low_prices[day]]
                
                all_new_data[day] = indv_data_list
                
        return all_new_data

# =====================================
# =========== MAIN FUNCTION ===========
# =====================================

#read_from_database_to_list(data_points = range(0,22)) # YOU NEED TO KEEP TRACK OF number of data_points --> Expected final number of data poins
check_file(22)
# Steps to add data
# 1. Make your function to calculate your new data points
# 2. Add your function to the data_collect function (two lines to add per new function)
# 3. Update the data_points value called in the main function (directly above)
# 4. PLZ COMMENT OUT YOUR LINE IN THE "data_collect" FUNCTION ONCE YOU HAVE CONFIRMED YOUR FILE IS GOOD