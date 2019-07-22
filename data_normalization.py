import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data.sampler import SubsetRandomSampler
import torch.utils.data as data
import numpy as np
import random
import math
import json

# ===========================================================
# ================= Random input generator ==================
# ===========================================================

# 9 input per day       --> dim 1
# 165 companies         --> dim 2
# ~763 days             --> dim 3

def random_input_gen(num_data_per_day = 9, num_companies = 165, num_days = 763): # random numbers ranging from +- 100,000,000,000 (100 billion)
    data = [[[None for k in range(num_data_per_day)] for j in range(num_companies)] for i in range(num_days)]
    for i in range(num_days):
        for j in range(num_companies):
            for k in range(num_data_per_day):
                data[i][j][k] = random.randint(-100000000000,100000000001)
    # Force numbers to ensure logarithmic normalization works
    data[0][0][0] = 15
    data[0][0][1] = 0.05
    return data

# ===========================================================
# ====================== Normalization ======================
# ===========================================================

# normalize_function = 0    --> No normalization
# normalize_function = 1    --> linear normalization
# normalize_function = 2    --> logarithmic normalization

# normalize_company = 0     --> normalize inside each company
# normalize_company = 1     --> normalize across all companies

# range = 0                 --> no limit
# range = 1                 --> [-1, 1]
# range = 2                 --> [ 0, 1]

def normalize_data(data, normalize_function = 0, normalize_company = 0, num_range = 0):
    
    if ((num_range != 0 and num_range != 1 and num_range != 2) or (normalize_company != 0 and normalize_company != 1) or (normalize_function != 0 and normalize_function != 1 and normalize_function != 2)):
        print("invalid input")
        return False

    if ((range == 1 or range == 2) and normalize_function == 0):
        print("cannot limit range with no normalization")
        return False
    
    if (range == 0 and normalize_function != 0):
        print("must limit range when normalizing data")
        return False
    
    num_days = len(data)
    num_companies = len(data[0])
    num_data_per_day = len(data[0][0])

    if (normalize_function == 2):      # Take the log 10 of all numbers if we perform logarithmic normalization, else linear do nothing
        for i in range(num_companies):
            for j in range(num_days):
                for k in range(num_data_per_day):
                    data[j][i][k] = log_normalization(data[j][i][k])
    
    if (normalize_company == 0):
        for i in range(num_companies): # each item is all of format [min, max]
            price, current_ratio, pps, eps, asset_turnover, pe_ratio, cash_flow, return_on_equity, working_capital = [0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0]
            for j in range(num_days):
                for k in range(num_data_per_day):
                    if (k == 0):
                        if (price[1] < data[j][i][k]):
                            price[1] = data[j][i][k]
                        if (price[0] > data[j][i][k]):
                            price[0] = data[j][i][k]
                    elif (k == 1):
                        if (current_ratio[1] < data[j][i][k]):
                            current_ratio[1] = data[j][i][k]
                        if (current_ratio[0] > data[j][i][k]):
                            current_ratio[0] = data[j][i][k]
                    elif (k == 2):
                        if (pps[1] < data[j][i][k]):
                            pps[1] = data[j][i][k]
                        if (pps[0] > data[j][i][k]):
                            pps[0] = data[j][i][k]
                    elif (k == 3):
                        if (eps[1] < data[j][i][k]):
                            eps[1] = data[j][i][k]
                        if (eps[0] > data[j][i][k]):
                            eps[0] = data[j][i][k]
                    elif (k == 4):
                        if (asset_turnover[1] < data[j][i][k]):
                            asset_turnover[1] = data[j][i][k]
                        if (asset_turnover[0] > data[j][i][k]):
                            asset_turnover[0] = data[j][i][k]
                    elif (k == 5):
                        if (pe_ratio[1] < data[j][i][k]):
                            pe_ratio[1] = data[j][i][k]
                        if (pe_ratio[0] > data[j][i][k]):
                            pe_ratio[0] = data[j][i][k]
                    elif (k == 6):
                        if (cash_flow[1] < data[j][i][k]):
                            cash_flow[1] = data[j][i][k]
                        if (cash_flow[0] > data[j][i][k]):
                            cash_flow[0] = data[j][i][k]
                    elif (k == 7):
                        if (return_on_equity[1] < data[j][i][k]):
                            return_on_equity[1] = data[j][i][k]
                        if (return_on_equity[0] > data[j][i][k]):
                            return_on_equity[0] = data[j][i][k]
                    elif (k == 8):
                        if (working_capital[1] < data[j][i][k]):
                            working_capital[1] = data[j][i][k]
                        if (working_capital[0] > data[j][i][k]):
                            working_capital[0] = data[j][i][k]
            # Normalize within a single company
            for j in range(num_days):
                for k in range(num_data_per_day):
                    if (k == 0):
                        data[j][i][k] = (data[j][i][k] - price[0]) / (price[1] - price[0])
                    elif (k == 1):
                        data[j][i][k] = (data[j][i][k] - current_ratio[0]) / (current_ratio[1] - current_ratio[0])
                    elif (k == 2):
                        data[j][i][k] = (data[j][i][k] - pps[0]) / (pps[1] - pps[0])
                    elif (k == 3):
                        data[j][i][k] = (data[j][i][k] - eps[0]) / (eps[1] - eps[0])
                    elif (k == 4):
                        data[j][i][k] = (data[j][i][k] - asset_turnover[0]) / (asset_turnover[1] - asset_turnover[0])
                    elif (k == 5):
                        data[j][i][k] = (data[j][i][k] - pe_ratio[0]) / (asset_turnover[1] - asset_turnover[0])
                    elif (k == 6):
                        data[j][i][k] = (data[j][i][k] - cash_flow[0]) / (cash_flow[1] - cash_flow[0])
                    elif (k == 7):
                        data[j][i][k] = (data[j][i][k] - return_on_equity[0]) / (return_on_equity[1] - return_on_equity[0])
                    elif (k == 8):
                        data[j][i][k] = (data[j][i][k] - working_capital[0]) / (working_capital[1] - working_capital[0])

    elif (normalize_company == 1):
        price, current_ratio, pps, eps, asset_turnover, pe_ratio, cash_flow, return_on_equity, working_capital = [0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0]
        for i in range(num_companies): # each item is all of format [min, max]
            for j in range(num_days):
                for k in range(num_data_per_day):
                    if (k == 0):
                        if (price[1] < data[j][i][k]):
                            price[1] = data[j][i][k]
                        if (price[0] > data[j][i][k]):
                            price[0] = data[j][i][k]
                    elif (k == 1):
                        if (current_ratio[1] < data[j][i][k]):
                            current_ratio[1] = data[j][i][k]
                        if (current_ratio[0] > data[j][i][k]):
                            current_ratio[0] = data[j][i][k]
                    elif (k == 2):
                        if (pps[1] < data[j][i][k]):
                            pps[1] = data[j][i][k]
                        if (pps[0] > data[j][i][k]):
                            pps[0] = data[j][i][k]
                    elif (k == 3):
                        if (eps[1] < data[j][i][k]):
                            eps[1] = data[j][i][k]
                        if (eps[0] > data[j][i][k]):
                            eps[0] = data[j][i][k]
                    elif (k == 4):
                        if (asset_turnover[1] < data[j][i][k]):
                            asset_turnover[1] = data[j][i][k]
                        if (asset_turnover[0] > data[j][i][k]):
                            asset_turnover[0] = data[j][i][k]
                    elif (k == 5):
                        if (pe_ratio[1] < data[j][i][k]):
                            pe_ratio[1] = data[j][i][k]
                        if (pe_ratio[0] > data[j][i][k]):
                            pe_ratio[0] = data[j][i][k]
                    elif (k == 6):
                        if (cash_flow[1] < data[j][i][k]):
                            cash_flow[1] = data[j][i][k]
                        if (cash_flow[0] > data[j][i][k]):
                            cash_flow[0] = data[j][i][k]
                    elif (k == 7):
                        if (return_on_equity[1] < data[j][i][k]):
                            return_on_equity[1] = data[j][i][k]
                        if (return_on_equity[0] > data[j][i][k]):
                            return_on_equity[0] = data[j][i][k]
                    elif (k == 8):
                        if (working_capital[1] < data[j][i][k]):
                            working_capital[1] = data[j][i][k]
                        if (working_capital[0] > data[j][i][k]):
                            working_capital[0] = data[j][i][k]
        # Normalize for all companies
        for i in range(num_companies):
            for j in range(num_days):
                for k in range(num_data_per_day):
                    if (k == 0):
                        data[j][i][k] = (data[j][i][k] - price[0]) / (price[1] - price[0])
                    elif (k == 1):
                        data[j][i][k] = (data[j][i][k] - current_ratio[0]) / (current_ratio[1] - current_ratio[0])
                    elif (k == 2):
                        data[j][i][k] = (data[j][i][k] - pps[0]) / (pps[1] - pps[0])
                    elif (k == 3):
                        data[j][i][k] = (data[j][i][k] - eps[0]) / (eps[1] - eps[0])
                    elif (k == 4):
                        data[j][i][k] = (data[j][i][k] - asset_turnover[0]) / (asset_turnover[1] - asset_turnover[0])
                    elif (k == 5):
                        data[j][i][k] = (data[j][i][k] - pe_ratio[0]) / (asset_turnover[1] - asset_turnover[0])
                    elif (k == 6):
                        data[j][i][k] = (data[j][i][k] - cash_flow[0]) / (cash_flow[1] - cash_flow[0])
                    elif (k == 7):
                        data[j][i][k] = (data[j][i][k] - return_on_equity[0]) / (return_on_equity[1] - return_on_equity[0])
                    elif (k == 8):
                        data[j][i][k] = (data[j][i][k] - working_capital[0]) / (working_capital[1] - working_capital[0])
    
    if (num_range == 1):
        for i in range(num_days):
            for j in range(num_companies):
                for k in range(num_data_per_day):
                    data[i][j][k] = (data[i][j][k] - 0.5) * 2.0
    return data

def log_normalization(x):
    if (x < 0):
        return -1 * math.log10((-1 * x) + 1)
    else:
        return math.log10(x + 1)

# ===========================================================================
# ========================= Labeling and Formatting =========================
# ===========================================================================

# Label = 1 increase in price
# Label = 0.5 no change in price (within percent error margin no_change_range)
# Label = 0 decrease in price

def add_labels(data, normalize_function = 2, normalize_company = 1, num_range = 1, pred_length = 5, no_change_range = 5):
    num_days = len(data)
    num_companies = len(data[0])

    # Label each input with the price 5 working days later
    labeled_data = []
    labeled_data_by_day =[]
    for i in range(num_days):
        for j in range(num_companies):
            if (num_days - i > pred_length):     # We can give a label
                if (data[i][j][0] < data[i + pred_length][j][0]*(1+(no_change_range/100.0))):     # Increase in price
                    label = 1
                elif (data[i][j][0] > data[i + pred_length][j][0]*(1-(no_change_range/100.0))):   # Decrease in price
                    label = 0
                else:                   # No change in price (range of allowance)
                    label = 0.5
            else:                       # We cannot give a label (no price 5 days ahead available yet)
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

def batch(data, batch_size = 16, train_size = 70, val_size = 15, test_size = 15, start_point_diff = 25, start_point_deviation = 5, length = 25, pred_length = 5, company_group = True, random_batch = False):
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
    if (company_group):                                     # All 200 companies at once (for finding relationship between companies)
        for i in times:                                         # Iterate through start days
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
    '''
    count = 0
    for i in train:
      print(i)
      count+=1
      if(count == 3):
        break
    ''' 
    train_data = data_to_tensor(train, company_group)
    val_data = data_to_tensor(val, company_group)
    test_data = data_to_tensor(test, company_group)
    
    return train_data, val_data,test_data

def data_to_tensor(batched_data, company_group):
    tensor_data = []
    if (company_group):
      for i in batched_data:
        item_tuple = (torch.FloatTensor(i[0]),torch.FloatTensor(i[1]))
        tensor_data.append(item_tuple)
    else:
      for i in batched_data:
        item_tuple = (torch.FloatTensor(i[0]),torch.FloatTensor(i[1]))
        tensor_data.append(item_tuple)
    return tensor_data

# ===========================================================
# ====================== Main Function ======================
# ===========================================================

# Normalization (default)
#   Logarithmic
#   across all companies
#   in range [-1,1]

def format_data(data, normalize_function = 2, normalize_company = 1, num_range = 1, batch_size = 16, train_size = 70, val_size = 15, test_size = 15, start_point_diff = 25, start_point_deviation = 5, length = 25, pred_length = 5, company_group = True, random_batch = False, no_change_range = 5):
    # Generate fake data for testing if no data is given
    if (data == None):
        # For fake data, assume dimension size
        num_data_per_day = 9
        num_companies = 165
        num_days = 763
        data = random_input_gen(num_data_per_day, num_companies, num_days)
    elif (data == True):
        with open("data_list_complete.json","r") as json_file:
            data = json.load(json_file)
    
    # Get length of data input
    num_data_per_day = len(data[0][0])
    num_companies = len(data[0])
    num_days = len(data)
    
    # Add Labels
    data = add_labels(data, normalize_function, normalize_company, num_range, pred_length, no_change_range)

    # Return batched the data 
    return batch(data, batch_size, train_size, val_size, test_size, start_point_diff, start_point_deviation, length, pred_length, company_group, random_batch)

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


# =================================================
# ==================== RUNNING ====================
# =================================================

# If data = None, we will generate random input
# If data = True, read the "data_list_complete.json file" --> Go to line 386 if under different name

# company_group = True, all companies at once
# company_group = False, one company at a time

data = None
train_data, val_data, test_data= format_data(data, normalize_function = 2, normalize_company = 1, num_range = 1, batch_size = 16, train_size = 70, val_size = 15, test_size = 15, start_point_diff = 25, start_point_deviation = 5, length = 25, pred_length = 5, company_group = True, random_batch = False, no_change_range = 5)

# DON'T FORGET YOU NEED TO DO:
# train_loader = torch.utils.data.DataLoader(train_data, batch_size=16)
# for train, val, test data