import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision.transforms as transforms
import torch.utils.data as data
import numpy as np
import random
import math
import json
import ast

# ===========================================================
# ================= Data Collecting Class ===================
# ===========================================================
class data_collect():
    def __init__(self, normalize_function = 2, normalize_company = 0, num_range = 1, train_size = 70, val_size = 15, test_size = 15, start_point_diff = 25, start_point_deviation = 5, length = 25, pred_length = 5, company_group = True, random_batch = False, no_change_range = 5, data_points = range(0,11)):
        self.normalize_function = normalize_function
        self.normalize_company = normalize_company
        self.num_range = num_range
        self.train_size = train_size
        self.val_size = val_size
        self.test_size = test_size
        self.start_point_diff = start_point_diff
        self.start_point_deviation = start_point_deviation  
        self.length = length
        self.pred_length = pred_length
        self.no_change_range = no_change_range
        self.company_group = company_group
        self.random_batch = random_batch
        self.data_points = data_points


    def format_data(self, data, filename):
        # Generate fake data for testing if no data is given
        if (data == None):  
            # For fake data, assume dimension size
            num_data_per_day = 8
            num_companies = 161
            num_days = 820
            data = random_input_gen(num_data_per_day, num_companies, num_days)
        elif (data == True):
            # Read data from .json file
            data = read_from_database_to_list(self.data_points, filename)
            # Get length of data input
            num_data_per_day = len(data[0][0])
            num_companies = len(data[0])
            num_days = len(data)
        
        
        # Add Labels
        data = add_labels(data, self.normalize_function, self.normalize_company, self.num_range, self.pred_length, self.no_change_range)

        # Return batched the data (3 tensors)
        return batch(data, self.train_size, self.val_size, self.test_size, self.start_point_diff, self.start_point_deviation, self.length, self.pred_length, self.company_group, self.random_batch)

    def get_label_frequency(self, data, dataset_type):
        data_loader = torch.utils.data.DataLoader(data, batch_size=16)
        zeros = 0
        ones = 0
        neg_one = 0
        for data_item, data_label in data_loader:
            label_to_count = data_label.tolist()
            for i in label_to_count:
                if (int(i) == -1):
                    neg_one += 1
                elif (int(i) == 1):
                    ones += 1
                elif (int(i) == 0):
                    zeros += 1
        print(neg_one)
        print(zeros)
        print(ones)
        print(dataset_type.upper() + " SET LABEL FREQUENCY")
        print("Percent of decrease label: ", neg_one / (zeros + ones + neg_one))
        print("Percent of neutral label:  ", zeros / (zeros + ones + neg_one))
        print("Percent of increase label: ", ones / (zeros + ones + neg_one))
        return True


# ===========================================================
# ================= Random input generator ==================
# ===========================================================

# 9 input per day       --> dim 1
# 165 companies         --> dim 2
# ~763 days             --> dim 3

def random_input_gen(num_data_per_day = 11, num_companies = 161, num_days = 820, data_points = range(0,11)): # random numbers ranging from +- 100,000,000,000 (100 billion)
    data = [[[None for k in range(num_data_per_day)] for j in range(num_companies)] for i in range(num_days)]
    for i in range(num_days):
        for j in range(num_companies):
            for k in range(num_data_per_day):
                data[i][j][k] = random.randint(-100000000000,100000000001)
    # Force numbers to ensure logarithmic normalization works
    data[0][0][0] = 15
    data[0][0][1] = 0.05
    return data

# ============================================================
# ===== Formatting data from .json to dictionary to list =====
# ============================================================

# data_points = list    --> Contains all indexes that are desired
#                                   ~~~ RATIOS ~~~
#                       --> 0 = EPS, 1 = PE ratio, 2 = PPS,
#                       --> 3 = asset turnover 4 = cash flow,
#                       --> 5 = current ratio, 6 = return on equity,
#                       --> 7 = working capital
#                                 ~~~ Stock Data ~~~
#                       --> 8 = Closing stock price,
#                       --> 9 = 14-day moving avg,
#                       --> 10 = 37-day moving average

def read_from_database_to_list(data_points = range(0,11), filename = "data_list_complete.json"):      # Take in raw str, and convert to dictionary, then to list
        with open(filename) as f:              # *******FILE LOCATION/NAME MAY DIFFER ACCORDING TO YOUR REQUIREMENTS******
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary

        data = data[0]

        list_companies = data["2019-07-17"].keys()              # All company symbols (anyday works after april 14th 2019)
        list_companies.sort(reverse = False)                    # Sort alphabetically company names

        list_days = data.keys()                                 # All database days
        list_days = sorted(list_days, key = sorting)            # Sort days in past -> future order
                
        bad_companies = ["WLKP", "VMC", "VRS", "REX"]           # These companies data are incomplete. To be removed (not enough data)
        bad_days = []                                           # List of incomplete days (mostly comprised of days before april 14th 2019)

        for day in list_days:                                   # Delete bad days and companies
                num_companies = len(data[day])
                for company in list_companies:
                        if (company in bad_companies and company in data[day]):
                                del data[day][company]
                        if (num_companies < 161):
                                del data[day]
                                bad_days.append(day)
                                break

        for company in bad_companies:                           # Remove bad companies from company list
                list_companies.remove(company)

        for day in bad_days:                                    # Remove bad days from days list
                list_days.remove(day)

        # Give AGX data for April 14th (accidentally omitted)
        data["2016-04-14"]["AGX"] = data["2016-04-15"]["AGX"]


        num_days = len(data)                                    # Dimensions of data
        num_companies = len(data["2016-04-14"])
        num_data_points = len(data["2016-04-14"]["AGX"])


        list_data = [[[0 for i in range(len(num_data_points))] for j in range(num_companies)] for k in range(num_days)]

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
        return list_data            # Type list with all requested data

def sorting(L):                     # Function to sort the days in chronological order
        splitup = L.split('-')
        return splitup[0], splitup[1], splitup[2]

# ===========================================================
# ====================== Normalization ======================
# ===========================================================

# normalize_function = 0    --> No normalization                (Baseline model did not train)
# normalize_function = 1    --> linear normalization            (Baseline model did not train)
# normalize_function = 2    --> logarithmic normalization       (Only function that works for baseline model)

# normalize_company = 0     --> normalize inside each company   (Only normalization that works for baseline model)
# normalize_company = 1     --> normalize across all companies  (Did not work for baseline model)

# range = 0                 --> no limit
# range = 1                 --> [-1, 1]
# range = 2                 --> [ 0, 1]

def normalize_data(data, normalize_function = 0, normalize_company = 0, num_range = 0):
    
    # Simple error checking
    if ((num_range != 0 and num_range != 1 and num_range != 2) or (normalize_company != 0 and normalize_company != 1) or (normalize_function != 0 and normalize_function != 1 and normalize_function != 2)):
        print("invalid input")
        return False

    if ((range == 1 or range == 2) and normalize_function == 0):
        print("cannot limit range with no normalization")
        return False
    
    if (range == 0 and normalize_function != 0):
        print("must limit range when normalizing data")
        return False
    
    num_days = len(data)                # Get data dimensions
    num_companies = len(data[0])
    num_data_per_day = len(data[0][0])

    if (normalize_function == 2):       # Take the log 10 of all numbers if we perform logarithmic normalization, else proceed to obtain max/min values
        for i in range(num_days):
            for j in range(num_companies):
                for k in range(num_data_per_day):
                    data[i][j][k] = log_normalization(data[i][j][k])
    
    # 2D list to record each max/min values for each input variable type (the 8 ratios and 3 stock price data)
    maxmin_values = [[0.0,0.0] for i in range(num_data_per_day)]

    if (normalize_company == 0):
        for i in range(num_companies):
            for j in range(num_days):
                for k in range(num_data_per_day):
                    if (maxmin_values[k][1] < data[j][i][k]):
                        maxmin_values[k][1] = data[j][i][k]
                    if (maxmin_values[k][0] > data[j][i][k]):
                        maxmin_values[k][0] = data[j][i][k]
                    
            # Normalize within a single company
            for j in range(num_days):
                for k in range(num_data_per_day):
                    try:
                        data[j][i][k] = (data[j][i][k] - maxmin[k][0]) / (maxmin[k][1] - maxmin[k][0])
                    except:
                        print("Error: DIVISION BY ZERO")
                        print("day number:     ", j)
                        print("company number: ", i)
                        print("data index:     ", k)

    elif (normalize_company == 1):
        for i in range(num_companies):
            for j in range(num_days):
                for k in range(num_data_per_day):
                    if (maxmin_values[k][1] < data[j][i][k]):
                        maxmin_values[k][1] = data[j][i][k]
                    if (maxmin_values[k][0] > data[j][i][k]):
                        maxmin_values[k][0] = data[j][i][k]
                    
        # Normalize for all data across all companies
        for i in range(num_companies):
            for j in range(num_days):
                for k in range(num_data_per_day):
                    try:
                        data[j][i][k] = (data[j][i][k] - maxmin[k][0]) / (maxmin[k][1] - maxmin[k][0])
                    except:
                        print("Error: DIVISION BY ZERO")
                        print("day number:     ", j)
                        print("company number: ", i)
                        print("data index:     ", k)

    # Normalize the range of the data
    if (num_range == 1):
        for i in range(num_days):
            for j in range(num_companies):
                for k in range(num_data_per_day):
                    data[i][j][k] = (data[i][j][k] - 0.5) * 2.0

    # Return normalize data of type list
    return data

def log_normalization(x):   # Log 10 normalization function
    if (x < 0):
        return -1 * math.log10((-1 * x) + 1)
    else:
        return math.log10(x + 1)

# ===========================================================================
# ========================= Labeling and Formatting =========================
# ===========================================================================

# Label = 1  increase in price
# Label = 0  no change in price (within percent error margin no_change_range)
# Label = -1 decrease in price

def add_labels(data, normalize_function = 2, normalize_company = 0, num_range = 1, pred_length = 5, no_change_range = 5, data_points = range(0,11)):
    # Get dimensions of data
    num_days = len(data)
    num_companies = len(data[0])

    # Get closing price's index
    if (8 not in data_points):
        print("Data does not contain closing stock price")
    price_index = data_points.index(8)

    # Label each input with the price 5 working days later
    labeled_data = []
    labeled_data_by_day =[]
    for i in range(num_days):
        for j in range(num_companies):
            if (num_days - i > pred_length):     # We can give a label
                if (data[i][j][price_index] > data[i + pred_length][j][price_index]*(1+(no_change_range/100.0))):     # Increase in price
                    label = -1
                elif (data[i][j][price_index] < data[i + pred_length][j][price_index]*(1-(no_change_range/100.0))):   # Decrease in price
                    label = 1
                else:                           # No change in price (range of allowance)
                    label = 0
            else:                               # We cannot give a label (no price 5 days ahead available yet)
                label = None
            labeled_data_by_day.append(label)
        labeled_data.append(labeled_data_by_day)
        labeled_data_by_day = []

    # Normalize the data
    normalized_data = normalize_data(data, normalize_function, normalize_company, num_range)

    # Add labels to the normalized data
    formatted_data = []
    for day in range(len(normalized_data)):
        formatted_day_data = []
        for company in range(len(normalized_data[day])):
            formatted_day_data.append([normalized_data[day][company], labeled_data[day][company]])
        formatted_data.append(formatted_day_data)

    # Return type list with labels attached
    return formatted_data

# ============================================================
# ========================= Batching =========================
# ============================================================

# random = False    --> means first 70% months are training, next 15% are validation
#                       and next 15% are test (assuming percentages did not change)
# random = True     --> randomly pick 70% of months, 15% of months, and 15% of months for 
#                       train/val/test data

# start_point_diff  --> how far apart are the first days in adjacent batchs

# train_size, val_size, test_size   --> percentage of batches to be in each set (must add to 100%)

# start_point_deviation --> the start_point can deviate +- 5 (for example) from the original start_point_diff it was set for

# length        --> how many days in one "item". Days being the days where the market is open for trade

# company_group = True  --> all 165 companies at once
# company_group = False --> 1 company at a time

def batch(data, train_size = 70, val_size = 15, test_size = 15, start_point_diff = 25, start_point_deviation = 5, length = 25, pred_length = 5, company_group = True, random_batch = False):
    # Ensure percentages add up properly
    if (train_size + val_size + test_size != 100):
        print("ensure train_size + val_size + test_size = 100%")
        return None, None, None

    num_days = len(data)
    num_companies = len(data[0])

    # Use start_point_diff, start_point_deviation, and length to get the day stamps we will cover
    times = []
    time_start = 0
    while((time_start + length + pred_length) < num_days):  # Note that the case where we deal with individual companies, we still give the same start date for each batch item
        times.append(time_start)
        time_start = time_start + start_point_diff
    
    for time in range(0,len(times)):
        if (times[time] != 0):
            times[time] += random.randint(-pred_length,pred_length)
   
    # Batching the data
    # Batch data according to start_point_diff, start_point_deviation, length, and company_group
    batched_data = []
    if (company_group):                                    # All 200 companies at once (for finding relationship between companies)
        for i in times:                                    # Iterate through start days
            single_batch = []
            price_label = []
            for day in range(i, i + length):               # Iterate through the length of data per item
                count = 0
                single_day = []
                for companies in range(num_companies):
                    for ratios in data[day][companies]:    # Iterate through all companies
                        if (type(ratios) is list):
                            single_day.append(ratios)
                            count += 1
                        elif ((type(ratios) is int or type(ratios) is float) and day == i + length - 1):
                            price_label.append(ratios)
                single_batch.append(single_day)
            batched_data.append([single_batch,price_label])
    else:                                                   # sOne company at a time (no relationship between companies)
        for i in times:                                         # Iterate through start days
            for companies in range(num_companies):               # Iterate through the length of data per item
                price_label = 0
                single_company = []
                for day in range(i, i + length):
                    for ratios in data[day][companies]:    # Iterate through all companies
                        if (type(ratios) is list):
                            single_company.append(ratios)
                        elif ((type(ratios) is int or type(ratios) is float) and day == i + length - 1):
                            price_label = ratios
                batched_data.append([single_company,price_label])
    train_val_split = int(len(batched_data)*train_size/100.0)
    val_test_split = int(len(batched_data)*(train_size + val_size)/100.0)

    train = batched_data[:train_val_split]
    val = batched_data[train_val_split:val_test_split]
    test = batched_data[val_test_split:]

    train_data = data_to_tensor(train, company_group)
    val_data = data_to_tensor(val, company_group)
    test_data = data_to_tensor(test, company_group)
    
    # Return 3 tensors
    return train_data, val_data, test_data

def data_to_tensor(batched_data, company_group):
    tensor_data = []
    if (company_group):
      for i in batched_data:
        item_tuple = (torch.FloatTensor(i[0]).cuda(),torch.tensor(i[1], dtype = torch.long).cuda())
        tensor_data.append(item_tuple)
    else:
      for i in batched_data:
        item_tuple = (torch.FloatTensor(i[0]).cuda(),torch.tensor(i[1], dtype = torch.long).cuda())
        tensor_data.append(item_tuple)
    # Return data tensor and label tensor together in a tuple
    return tensor_data

# ===========================================================
# ====================== Main Function ======================
# ===========================================================

# Normalization (default)
#   Logarithmic
#   across all companies
#   in range [-1,1]



# ===================================================================
# ==================== EXPLANATION OF PARAMETERS ====================
# ===================================================================

# ------ Data Dimensions ------
# 9 input per day       --> dim 1 (if we only want to do stock prices, we can extract it ourselves)
# 165 companies         --> dim 2
# ~763 days             --> dim 3
 
# ------ Data input ------
# data = None       (randomly generate between -100 billion and 100 billion)
# data = Some_list  (normal input)

# ------ Normalization ------
# normalize_function = 0    (no normalization)
# normalize_function = 1    (linear normalization) --> Horibly failed for random case, prob for real case too
# normalize_function = 2    (logarithmic normalization)

# normalize_company = 0     (normalize within each company)
# normalize_company = 1     (normalize across all companies)

# num_range = 0             (no normalization range)
# num_range = 1             (normalization range [-1,1])
# num_range = 2             (normalization range [0,1])

# ------ Batching ------
# start_point_diff = m          (m working days between two adjacent batch items) --> Influences size of train/val/test dataset
#                               ex. start_point_diff = 25                                   -->     start_days = [0,25,50,75,100,...]
# start_point_deviation = n     (+- n days for deviation from the evenly split start points. Cannot go below 0.)
#                               ex. start_point_diff = 25, start_point_deviation = 5        -->     start_days = [2,24,55,70,100...]
# pred_length = x               (x days worth of data history per item)
# company_group = True          Batch items by all companies in one set. Will produce a label of size [num_companies]   
#                               -->     less train/val/test data (but potentially learns company relations)
# comapny_group = False         Batch items by individual company. Will produce a label of size 1
#                               -->     more train/val/test data (but no company relations)
# random = True                 split train/val/test set randomly (no chronological order)
# random = False                split train/val/test set chrnologically (train fist, then validation, then test)

# ------ Labeling ------
# no_change_range = x           (+-x% deviation is to be considered that the price has not changed)
# ~below are not parameters, but just the label in the data~
# label = 0                     (decrease in price)
# label = 0.5                   (no change in price, within the error margin no_change_range)
# label = 1                     (increase in price)
# Note: depending on company_group = True / False, the label may be a single number after each batch item, or a 1D-list of size num_companies

