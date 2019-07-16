import os
import pandas as pd
import csv
import shutil
import json
import ast
import datetime  
from datetime import timedelta 

# ==================================
# ========= MAIN FUNCTION ==========
# ==================================

def extract_data(start = 0, end = 165, file_count = 14): 
        wrk_directory = os.getcwd()
        bad_comp = ["LEN", "GMO", "NG", "TMQ", "UEC", "VGZ", "WWR", "XPL"]    # Excluded as no net sales/revenue reported or assets/liabilities explicit
        all_data = []
        symbol_count = 0
        remove_bad_files()                                              # Move non-american with less than 3 year IPO (14 files) to obsolete folder
        for dirpath, dirnames, files in os.walk('.\Quarterly Reports'):
                count = 0
                if (symbol_count >= start and symbol_count <= end):     # Only search the indexs of the companies
                        for file_name in files:
                                if (file_name[-5:] in ".xlsx" and dirpath[21:] not in bad_comp):
                                        file = wrk_directory + dirpath[1:] + "\\" + file_name           # File Location
                                        single_comp_file = get_numbers(file,dirpath[20:],file_name[:10])  # Extracting Numbers
                                        all_data.append(get_ratios(single_comp_file))
                                if (count == file_count):               # Number of files per company
                                        break
                                count = count + 1
                        print(symbol_count, ": ", dirpath[20:])                         
                elif (symbol_count > end):
                        break
                symbol_count = symbol_count + 1
        return all_data

# =============================================================================
# ====== Removing Non-American Symbols with less than 3 year IPO history ======
# =============================================================================

def remove_bad_files():                 # Remove all company symbol folders with less than 14 financial statements and Non-american
        wrk_directory = os.getcwd()
        
        with open('None_USA_Stock_Symbols.json') as json_file:  # get non-american stock symbols dictionary 
                data = json.load(json_file)   
        non_american_symbols = []
        
        for i in data:
                non_american_symbols.append(data[i])                                    # format from dict to list    
                
        start = True                                                                    # Help identify to skip first file (\Quaterly Reports)
        for dirpath, dirnames, files in os.walk('.\Quarterly Reports'):
                count = 0
                for file_name in files:
                        if (file_name[-5:] in ".xlsx"):                                 # Only take .xlsx files
                                count = count + 1                        
                if (start == False):
                        if (count < 14 or dirpath[1:] in non_american_symbols):         # Identify bad symbols
                                old_directory = wrk_directory + dirpath[1:]             # Bad file source
                                new_directory = wrk_directory + "\\Obsolete_symbols"    # Bad file destination
                                shutil.move(old_directory, new_directory)               # Move bad symbols to obsolete folder
                start = False
        return True


# ===================================
# ==== Extracting Ratios/Numbers ====
# ===================================

def get_numbers(filename, symbol, date):
        # [Net Profit, Sales, Profit Margins, Cash Flow, Short-term Debt, Long-term Debt, A/R Turnover, BEP,
        #  Dividends Paid]
        dfs = pd.read_excel(filename, sheet_name = list(range(0,10)))
        
        
        multiplier = {'$ in Thousands':1000, '$ in Millions':1000000, '$ in Billions':1000000000}
        multiplier_sh = {'shares in Thousands':1000, 'shares in Millions':1000000, 'shares in Billions':1000000000}
        
        # Identify which excel sheet is acquainted with which type of statement
        balance_sheet = []
        cash_sheet = []
        operations_sheet = []
        entity_sheet = []
        
        # Balance Sheet Data
        current_assets = []             # "Total current assets"
        current_liabilities = []        # "Total current liability"
        total_assets = []               # "Total assets"
        shares_outstanding = []         # "Common stock, outstanding" ***For EPS (a little more complicated)
        preferred_outstanding = []      # "Preferred stock, outstanding" ***For EPS (a little more complicated)
        total_shareholder_equity = []   # "Total Shareholder's equity"
        
        # Operations Sheet Data
        net_sales = []                  # Look for Net_sales (so gonna break)
        
        # Cash Flow Data
        net_income = []                 # "Net income"
        cash_beg = []                   # "Cash beginning" ***Just take from other file
        cash_end = []                   # "Cash ending"
        
        # Pages where certain numbers are found (if possibility found on multiple pages)
        PO_page = None
        SO_page = None
        NS_page = None       
        NI_page = None        
        
        # ==== PARSING FOR PAGE MULTIPLIERS AND PAGE CATEGORIES ====
        
        for i in range(0,10): # 10 IS A VERY ARBITRARY NUMBER
                money_mult = 1
                share_mult = 1    
                months = 1
                
                if ("$ in Thousands" in dfs[i].columns[0]):
                        money_mult = multiplier["$ in Thousands"]
                elif ("$ in Millions" in dfs[i].columns[0]):
                        money_mult = multiplier["$ in Millions"]
                elif ("$ in Billions" in dfs[i].columns[0]):
                        money_mult = multiplier["$ in Billions"]  
                        
                if ("shares in Thousands" in dfs[i].columns[0]):
                        share_mult = multiplier_sh["shares in Thousands"]
                elif ("shares in Millions" in dfs[i].columns[0]):
                        share_mult = multiplier_sh["shares in Millions"]
                elif ("shares in Billions" in dfs[i].columns[0]):
                        share_mult = multiplier_sh["shares in Billions"]   
                
                if ("3 months" in dfs[i].columns[1].lower()):
                        months = 3
                elif ("6 months" in dfs[i].columns[1].lower()):
                        months = 6
                elif ("9 months" in dfs[i].columns[1].lower()):
                        months = 9
                elif ("12 months" in dfs[i].columns[1].lower()):
                        months = 12
                        
                if ("balance" in dfs[i].columns[0].lower() or "financial position" in dfs[i].columns[0].lower()):
                        balance_sheet.append([i, money_mult, share_mult])
                elif (("operations" in dfs[i].columns[0].lower()) or ("income" in dfs[i].columns[0].lower()) or ("operating" in dfs[i].columns[0].lower()) or ("earnings" in dfs[i].columns[0].lower()) or ("comprehensive" in dfs[0].columns[0].lower())):   
                        operations_sheet.append([i, money_mult, share_mult, months])
                elif ("flow" in dfs[i].columns[0].lower()):
                        cash_sheet.append([i, money_mult, share_mult, months])
                elif ("entity" in dfs[i].columns[0].lower()):
                        entity_sheet.append([i, money_mult, share_mult, months])
        
        # ==== PARSING FOR NUMBERS IN THE SHEETS ====
        
        # Getting Balance Sheet Info
        for i in dfs[balance_sheet[0][0]].values:
                if (type(i[0]) is str):
                        if (((type(i[1]) == None or type(i[1]) == str) or i[1] != i[1]) and ((type(i[2]) != None or str) and i[2] == i[2])):
                                if (("total current assets" in i[0].lower() or ("current assets" in i[0].lower() and "other" not in i[0].lower())) and ("non" not in i[0].lower()) and ("discontinued" not in i[0].lower()) and ("held" not in i[0].lower())):
                                        current_assets.append(i[2])
                                elif (len(current_assets) == 0 and "current" in i[0].lower() and "total" in i[0].lower() and "assets" in i[0].lower() and "other" not in i[0].lower() and "non" not in i[0].lower() and "discontinued" not in i[0].lower() and "held" not in i[0].lower()):
                                        current_assets.append(i[2])
                                elif ("total current liabilities" in i[0].lower() or ("current liabilities" in i[0].lower() and "other" not in i[0].lower() and "non" not in i[0].lower()) and ("held" not in i[0].lower()) and ("discontinued" not in i[0].lower()) and ("disposed" not in i[0].lower())):
                                        current_liabilities.append(i[2])
                                elif ("liabilities, current" in i[0].lower() and "discontinued" not in i[0].lower() and "discount" not in i[0].lower and "accrued" not in i[0].lower() and len(current_liabilities) == 0):
                                        current_liabilities.append(i[2])
                                elif ("liabilties" in i[0].lower() and "current" in i[0].lower() and "total" in i[0].lower() and len(current_liabilities) == 0):
                                        current_liabilities.append(i[2])
                                elif ("total assets" in i[0].lower()):
                                        total_assets.append(i[2])
                                elif (len(total_assets) == 0 and "total" in i[0].lower() and "asset" in i[0].lower() and "current" not in i[0].lower() and "other" not in i[0].lower()):
                                        total_assets.append(i[2])
                                elif (("common stock" in i[0].lower() and "outstanding" in i[0].lower()) or ("limited partners" in i[0].lower() and ("preferred" not in i[0].lower())) and ("capital" not in i[0].lower())): # So bad
                                        shares_outstanding.append(i[2])
                                        SO_page = 0
                                elif (("common stock" in i[0].lower() or "weighted average number of shares outstanding" in i[0].lower()) and len(shares_outstanding) == 0):
                                        shares_outstanding.append(i[2])
                                        SO_page = 0
                                elif (("preferred stock" in i[0].lower() and "outstanding" in i[0].lower()) or ("preferred shares" in i[0].lower())):
                                        preferred_outstanding.append(i[2])
                                        PO_page = 0
                                elif ("total" in i[0].lower() and "equity" in i[0].lower() and "liabilities" not in i[0].lower() and ("stockholder" in i[0].lower() or "shareholder" in i[0].lower()) and "treasury" not in i[0].lower() and "interest" not in i[0].lower() and "group" not in i[0].lower()):
                                        total_shareholder_equity.append(i[2])
                                elif (("total equity" in i[0].lower() or "total stockholders'" in i[0].lower() or "shareholders' equity" in i[0].lower() or "stockholders' equity" in i[0].lower()) and len(total_shareholder_equity) == 0 and "treasury" not in i[0].lower() and "interest" not in i[0].lower() and "group" not in i[0].lower()):
                                        total_shareholder_equity.append(i[2])
                                elif ("deficit" in i[0].lower() and ("shareholders'" in i[0].lower() or "stockholders'" in i[0].lower()) and "group" not in i[0].lower() and ("liabilities" not in i[0].lower())):
                                        total_shareholder_equity.append(i[2])   
                                elif ((("total partners" in i[0].lower() and "capital" in i[0].lower()) or ("total deficit" in i[0].lower())) and len(total_shareholder_equity) == 0):
                                        total_shareholder_equity.append(i[2])                                
                        elif (type(i[1]) != None and (i[1] == i[1])):
                                if (("total current assets" in i[0].lower() or ("current assets" in i[0].lower() and "other" not in i[0].lower())) and ("non" not in i[0].lower()) and ("discontinued" not in i[0].lower()) and ("held" not in i[0].lower())):
                                        current_assets.append(i[1])
                                elif (len(current_assets) == 0 and "current" in i[0].lower() and "total" in i[0].lower() and "assets" in i[0].lower() and "other" not in i[0].lower() and "non" not in i[0].lower() and "discontinued" not in i[0].lower() and "held" not in i[0].lower()):
                                        current_assets.append(i[1])                                
                                elif ("total current liabilities" in i[0].lower() or ("liabilities, current" in i[0].lower()) or ("current liabilities" in i[0].lower() and "other" not in i[0].lower() and "non" not in i[0].lower()) and ("held" not in i[0].lower()) and ("discontinued" not in i[0].lower()) and ("disposed" not in i[0].lower())):
                                        current_liabilities.append(i[1])
                                elif ("liabilities, current" in i[0].lower() and "discontinued" not in i[0].lower() and "discount" not in i[0].lower and "accrued" not in i[0].lower() and len(current_liabilities) == 0):
                                        current_liabilities.append(i[1])
                                elif ("liabilties" in i[0].lower() and "current" in i[0].lower() and "total" in i[0].lower() and len(current_liabilities) == 0):
                                        current_liabilities.append(i[1])                                
                                elif ("total assets" in i[0].lower()):
                                        total_assets.append(i[1])
                                elif (len(total_assets) == 0 and "total" in i[0].lower() and "asset" in i[0].lower() and "current" not in i[0].lower() and "other" not in i[0].lower()):
                                        total_assets.append(i[1])                                
                                elif (("common stock" in i[0].lower() and "outstanding" in i[0].lower()) or ("limited partners" in i[0].lower() and ("preferred" not in i[0].lower())) and ("capital" not in i[0].lower())):
                                        shares_outstanding.append(i[1])
                                        SO_page = 0
                                elif (("common stock" in i[0].lower() or "weighted average number of shares outstanding" in i[0].lower()) and len(shares_outstanding) == 0):
                                        shares_outstanding.append(i[1])
                                        SO_page = 0
                                elif (("preferred stock" in i[0].lower() and "outstanding" in i[0].lower()) or ("preferred shares" in i[0].lower())):
                                        preferred_outstanding.append(i[1])
                                        PO_page = 0
                                elif ("total" in i[0].lower() and "equity" in i[0].lower() and "liabilities" not in i[0].lower() and ("stockholder" in i[0].lower() or "shareholder" in i[0].lower()) and ("treasury" not in i[0].lower() and "interest" not in i[0].lower() and "group" not in i[0].lower())):
                                        total_shareholder_equity.append(i[1])
                                elif (("total equity" in i[0].lower() or "total stockholders'" in i[0].lower() or "shareholders' equity" in i[0].lower() or "stockholders' equity" in i[0].lower()) and len(total_shareholder_equity) == 0 and "treasury" not in i[0].lower() and "interest" not in i[0].lower() and "group" not in i[0].lower()):
                                        total_shareholder_equity.append(i[1])
                                elif (("deficit" in i[0].lower()) and ("shareholders'" in i[0].lower() or "stockholders’" in i[0].lower()) and ("group" not in i[0].lower()) and ("liabilities" not in i[0].lower())):
                                        total_shareholder_equity.append(i[1])
                                elif ((("total partners" in i[0].lower() and "capital" in i[0].lower()) or ("total deficit" in i[0].lower())) and len(total_shareholder_equity) == 0):
                                        total_shareholder_equity.append(i[1])
        ttl_liabilities_temp = 0
        ttl_liabilities_and_equity_temp = 0
        if (len(total_shareholder_equity) == 0):                # If total shareholder equity not explicitly written
                for i in dfs[balance_sheet[0][0]].values:       # do total liabilities and equity - total liabilities
                        if (type(i[0]) is str):
                                if (((type(i[1]) == None or type(i[1]) == str) or i[1] != i[1]) and ((type(i[2]) != None or str) and i[2] == i[2])):
                                        if (i[0].lower() in "liabilities" or "total liabilities" in i[0]):
                                                ttl_liabilities_temp = i[2]
                                        elif (i[0].lower() in "liabilities and equity" or i[0].lower() in "equity and liabilities" or ("total" in i[0].lower() and "liabilities" in i[0].lower() and "equity" in i[0].lower())):
                                                ttl_liabilities_and_equity_temp = i[2]
                                        elif (len(total_assets) == 0 and i[0].lower() in "assets"):
                                                total_assets.append(i[2])
                                elif (type(i[1]) != None and (i[1] == i[1])):
                                        if (i[0].lower() in "liabilities" or "total liabilities" in i[0]):
                                                ttl_liabilities_temp = i[1]
                                        elif (i[0].lower() in "liabilities and equity" or i[0].lower() in "equity and liabilities" or ("total" in i[0].lower() and "liabilities" in i[0].lower() and "equity" in i[0].lower())):
                                                ttl_liabilities_and_equity_temp = i[1]
                                        elif (len(total_assets) == 0 and i[0].lower() in "assets"):
                                                total_assets.append(i[1])   
                if (ttl_liabilities_temp != 0 and ttl_liabilities_and_equity_temp != 0):
                        total_shareholder_equity = [ttl_liabilities_and_equity_temp - ttl_liabilities_temp]
                        
        if (len(total_assets) == 0):                            # If total assets is written under a category names assets, next to a box called "total"
                for i in dfs[balance_sheet[0][0]].values:
                        if (type(i[0]) is str):
                                if (((type(i[1]) == None or type(i[1]) == str) or i[1] != i[1]) and ((type(i[2]) != None or str) and i[2] == i[2])):
                                        if (i[0].lower() in "total"):
                                                total_assets.append(i[2])
                                                break
                                elif (type(i[1]) != None and (i[1] == i[1])):        
                                        if (i[0].lower() in "total"):
                                                total_assets.append(i[1])    
                                                break
        
        series_a = True
        common_issued = 0
        treasury = 0
        
        if (len(shares_outstanding) == 0):                      # If common outstanding mentioned as something else on 1st balance sheet page
                for i in dfs[balance_sheet[0][0]].values:
                        if (type(i[0]) == str):
                                if (((type(i[1]) == None or type(i[1]) == str) or i[1] != i[1]) and ((type(i[2]) != None or str) and i[2] == i[2])):
                                        if (("common" in i[0].lower() or "ordinary" in i[0].lower()) and "issued" in i[0].lower() and series_a):
                                                common_issued = i[2]
                                                series_a = False
                                        elif ("treasury" in i[0].lower() and "stock" in i[0].lower() and len(shares_outstanding) == 0):
                                                treasury = i[2]
                                elif (type(i[1]) != None and i[1] == i[1]):
                                        if (("common" in i[0].lower() or "ordinary" in i[0].lower()) and "issued" in i[0].lower() and series_a):
                                                common_issued = i[1]
                                                series_a = False
                                        elif ("treasury" in i[0].lower() and "stock" in i[0].lower() and len(shares_outstanding) == 0):
                                                treasury = i[1]                                
                if (common_issued != 0):
                        shares_outstanding.append([common_issued - treasury]) 
                        SO_page = 0
                        
        series_a = True
        if (len(balance_sheet) >= 2):                   # If common outstanding is mentioned on 2nd page (more reliable)
                for i in dfs[balance_sheet[1][0]].values:
                        if ((type(i[0]) is str) and (type(i[1]) != None) and (i[1] == i[1]) and type(i[1]) != str):
                                if ("common" in i[0].lower() and "outstanding" in i[0].lower() and series_a and int(i[1]) != 0):
                                        shares_outstanding = [i[1]] # OVERWRITE FIRST STATEMENT
                                        SO_page = 1
                                        series_a = False
                                elif ("preferred" in i[0].lower() and "outstanding" in i[0].lower()):
                                        preferred_outstanding = [i[1]] # OVEWRITE FIRST STATEMENT
                                        PO_page = 1
                                elif ((("common" in i[0].lower() and "shares" in i[0].lower()) or "unit" in i[0].lower()) and "issued" in i[0].lower() and len(shares_outstanding) == 0):
                                        common_issued = i[1]
                                elif ("treasury" in i[0].lower() and "stock" in i[0].lower() and len(shares_outstanding) == 0):
                                        treasury = i[1]
                if (common_issued != 0):
                        shares_outstanding.append([common_issued - treasury])
                        SO_page = 1
                
                for i in dfs[balance_sheet[1][0]].values:
                        if ((type(i[0]) is str) and (type(i[1]) != None) and (i[1] == i[1])):
                                if ("shares" in i[0].lower() and "outstanding" in i[0].lower() and len(shares_outstanding) == 0):
                                        shares_outstanding = [i[1]] # OVERWRITE FIRST STATEMENT
                                        SO_page = 1
                        
        try:
                for i in dfs[cash_sheet[0][0]].values:  # Check cash flow statement for net income, beginning and ending cash
                        if (type(i[0]) is str):
                                if ((type(i[1]) == None or i[1] != i[1] or type(i[1]) == str) and (type(i[2]) != None and i[2] == i[2])):
                                        if (("net" in i[0].lower() and ("income" in i[0].lower() or "earning" in i[0].lower())) and ("tax" not in i[0].lower()) and ("expense" not in i[0].lower()) and ("to" not in i[0].lower()) and ("dividend" not in i[0].lower()) and ("interest" not in i[0].lower()) and ("other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                net_income.append(i[2])
                                                NI_page = 0
                                        elif (((("cash" in i[0].lower() and "cash equivalents" in i[0].lower() or "cash and cash items" in i[0].lower()) and ("dividend" not in i[0].lower()) and "interest" not in i[0].lower()) and ("end" in i[0].lower() or "carrying value" in i[0].lower())) or i[0].lower() in "ending balance"):
                                                cash_end.append(i[2])
                                        elif (((("cash" in i[0].lower() and "end" in i[0].lower()) or ("end" in i[0].lower() and "period" in i[0].lower())) and ("dividend" not in i[0].lower())) or ("of year" in i[0].lower() and "end" in i[0].lower()) and len(cash_end) == 0 and ("interest" not in i[0].lower())):
                                                cash_end.append(i[2])  
                                        elif ((("cash and cash equivalents" in i[0].lower() or "cash and cash items" in i[0].lower()) and "beg" in i[0].lower() and ("dividend" not in i[0].lower()) and ("interest" not in i[0].lower())) or i[0].lower() in "beginning balance"):
                                                cash_beg.append(i[2])
                                        elif ((((("cash" in i[0].lower() and "beginning" in i[0].lower()) or ("beginning" in i[0].lower() and "period" in i[0].lower()) or ("beginning of year" in i[0].lower())) and ("dividend" not in i[0].lower()))) and len(cash_beg) == 0 and ("interest" not in i[0].lower())):
                                                cash_beg.append(i[2])
                                elif (type(i[1]) != None and i[1] == i[1]):
                                        if (("net" in i[0].lower() and ("income" in i[0].lower() or "earning" in i[0].lower())) and ("tax" not in i[0].lower()) and ("expense" not in i[0].lower()) and ("to" not in i[0].lower()) and ("dividend" not in i[0].lower()) and ("interest" not in i[0].lower()) and ("other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                net_income.append(i[1])
                                                NI_page = 0
                                        elif (((("cash" in i[0].lower() and "cash equivalents" in i[0].lower() or "cash and cash items" in i[0].lower()) and ("dividend" not in i[0].lower()) and "interest" not in i[0].lower()) and ("end" in i[0].lower() or "carrying value" in i[0].lower())) or i[0].lower() in "ending balance"):
                                                cash_end.append(i[1])
                                        elif ((((("cash" in i[0].lower() and "end" in i[0].lower()) or ("end" in i[0].lower() and "period" in i[0].lower())) and ("dividend" not in i[0].lower())) or ("of year" in i[0].lower() and "end" in i[0].lower())) and len(cash_end) == 0 and ("interest" not in i[0].lower())):
                                                cash_end.append(i[1]) 
                                        elif ((("cash and cash equivalents" in i[0].lower() or "cash and cash items" in i[0].lower()) and "beg" in i[0].lower() and ("dividend" not in i[0].lower()) and ("interest" not in i[0].lower())) or i[0].lower() in "beginning balance"):
                                                cash_beg.append(i[1])    
                                        elif (((("cash" in i[0].lower() and "beginning" in i[0].lower()) or ("beginning" in i[0].lower() and "period" in i[0].lower()) or ("beginning of year" in i[0].lower())) and ("dividend" not in i[0].lower())) and len(cash_beg) == 0 and ("interest" not in i[0].lower())):
                                                cash_beg.append(i[1])
        except:
                for i in dfs[cash_sheet[0][0]].values:
                        if (type(i[0]) is str):
                                if (type(i[1]) != None and i[1] == i[1]):
                                        if (("net" in i[0].lower() and ("income" in i[0].lower() or "earning" in i[0].lower())) and ("tax" not in i[0].lower()) and ("expense" not in i[0].lower()) and ("to" not in i[0].lower()) and ("dividend" not in i[0].lower()) and ("interest" not in i[0].lower()) and ("other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                net_income.append(i[1])
                                                NI_page = 0
                                        elif (((("cash" in i[0].lower() and "cash equivalents" in i[0].lower() or "cash and cash items" in i[0].lower()) and ("dividend" not in i[0].lower()) and "interest" not in i[0].lower()) and ("end" in i[0].lower() or "carrying value" in i[0].lower())) or i[0].lower() in "ending balance"):
                                                cash_end.append(i[1])
                                        elif ((((("cash" in i[0].lower() and "end" in i[0].lower()) or ("end" in i[0].lower() and "period" in i[0].lower())) and ("dividend" not in i[0].lower())) or ("of year" in i[0].lower() and "end" in i[0].lower())) and len(cash_end) == 0 and ("interest" not in i[0].lower())):
                                                cash_end.append(i[1]) 
                                        elif ((("cash and cash equivalents" in i[0].lower() or "cash and cash items" in i[0].lower()) and "beg" in i[0].lower() and ("dividend" not in i[0].lower()) and ("interest" not in i[0].lower())) or i[0].lower() in "beginning balance"):
                                                cash_beg.append(i[1])    
                                        elif (((("cash" in i[0].lower() and "beginning" in i[0].lower()) or ("beginning" in i[0].lower() and "period" in i[0].lower()) or ("beginning of year" in i[0].lower())) and ("dividend" not in i[0].lower())) and len(cash_beg) == 0 and ("interest" not in i[0].lower())):
                                                cash_beg.append(i[1])                
        change_in_cash = 0;
        if (len(cash_beg) == 0):
                for i in dfs[cash_sheet[0][0]].values:
                        if (type(i[0]) is str):
                                if ((type(i[1]) == None or i[1] != i[1] or type(i[1]) == str) and (type(i[2]) != None and i[2] == i[2])):        
                                        if (("cash and cash equivalent" in i[0].lower() or "cash and cash item" in i[0].lower()) and ("period" in i[0].lower()) and ("increase" in i[0].lower() or "decrease" in i[0].lower())): 
                                                change_in_cash = i[2]
                                elif (type(i[1]) != None and i[1] == i[1]):    
                                        if (("cash and cash equivalent" in i[0].lower() or "cash and cash item" in i[0].lower()) and ("period" in i[0].lower()) and ("increase" in i[0].lower() or "decrease" in i[0].lower())): 
                                                change_in_cash = i[1]
                if (len(cash_end) != 0):
                        cash_beg = [max(cash_end) - change_in_cash]
                                                
        months = ["january","february","march","april","may","june","july","august","september","october","november","december"]
        next = True
        if (len(cash_beg) == 0):                        # More checks for beginning and ending cash values
                for i in dfs[cash_sheet[0][0]].values:
                        if (type(i[0]) is str):
                                if ((type(i[1]) == None or i[1] != i[1] or type(i[1]) == str) and (type(i[2]) != None and i[2] == i[2])): 
                                        for month in months:
                                                if (month in i[0].lower()):
                                                        cash_beg.append(i[2])
                                                        break
                                                elif (len(cash_beg) == 1 and next):
                                                        cash_end.append(i[2])
                                                        next = False
                                                        break
                                elif (type(i[1]) != None and i[1] == i[1]):
                                        for month in months:
                                                if (month in i[0].lower()):
                                                        cash_beg.append(i[1])
                                                        break
                                                elif (len(cash_beg) == 1 and next):
                                                        cash_end.append(i[2])
                                                        next = False
                                                        break
                                        
        try:
                for i in dfs[operations_sheet[0][0]].values:    # Check first operations sheet for net sales (or revenue) and net income
                        if (type(i[0]) is str):
                                if ((type(i[1]) == None or type(i[1]) == str or i[1] != i[1]) and (type(i[2]) != None and i[2] == i[2])):
                                        if ("net sales" in i[0].lower() or "total revenue" in i[0].lower()):
                                                if ("total" in i[0].lower()):
                                                        net_sales = [i[2]]
                                                        NS_page = 0                                                
                                                else:
                                                        net_sales.append(i[2])
                                                        NS_page = 0                                                
                                        elif (("sales" in i[0].lower() or "revenue" in i[0].lower()) and len(net_sales)==0):
                                                net_sales.append(i[2])
                                                NS_page = 0                                        
                                        elif ("total net sales" in i[0].lower()):
                                                net_sales = [i[2]] # OVERWRITE
                                                NS_page = 0
                                        elif (("net" in i[0].lower()) and ("loss" in i[0].lower() or "income" in i[0].lower() or "gain" in i[0].lower()) and ("tax" not in i[0].lower() and "discontinued" not in i[0].lower() and "share" not in i[0].lower() and "attributable" not in i[0].lower() and "other" not in i[0].lower())  and ("miscellaneous" not in i[0].lower())):
                                                net_income.append(i[2])  
                                                NI_page = 1
                                elif (type(i[1]) != None and type(i[1]) != str and (i[1] == i[1])):
                                        if ("net sales" in i[0].lower() or "total revenue" in i[0].lower()):
                                                if ("total" in i[0].lower()):
                                                        net_sales = [i[1]]
                                                        NS_page = 0
                                                else:
                                                        net_sales.append(i[1])
                                                        NS_page = 0
                                        elif (("sales" in i[0].lower() or "revenue" in i[0].lower()) and len(net_sales)==0):
                                                net_sales.append(i[1])   
                                                NS_page = 0
                                        elif (("net" in i[0].lower()) and ("loss" in i[0].lower() or "income" in i[0].lower() or "gain" in i[0].lower()) and ("tax" not in i[0].lower() and "discontinued" not in i[0].lower() and "share" not in i[0].lower() and "attributable" not in i[0].lower() and "other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                net_income.append(i[1])  
                                                NI_page = 1
        except:
                try:
                        for i in dfs[operations_sheet[0][0]].values:
                                if (type(i[0]) is str):
                                        if (type(i[1]) != None and type(i[1]) != str and (i[1] == i[1])):
                                                if ("net sales" in i[0].lower() or "total revenue" in i[0].lower()):
                                                        if ("total" in i[0].lower()):
                                                                net_sales = [i[1]]
                                                                NS_page = 0
                                                        else:
                                                                net_sales.append(i[1])
                                                                NS_page = 0
                                                elif (("sales" in i[0].lower() or "revenue" in i[0].lower()) and len(net_sales)==0):
                                                        net_sales.append(i[1])   
                                                        NS_page = 0
                                                elif (("net" in i[0].lower()) and ("loss" in i[0].lower() or "income" in i[0].lower() or "gain" in i[0].lower()) and ("tax" not in i[0].lower() and "discontinued" not in i[0].lower() and "share" not in i[0].lower() and "attributable" not in i[0].lower() and "other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                        net_income.append(i[1])  
                                                        NI_page = 1     
                except:
                        second_fail = True
        try:                              
                if (len(operations_sheet) > 1 and len(net_sales) == 0):
                        for i in dfs[operations_sheet[1][0]].values:
                                if (type(i[0]) is str):
                                        if ((type(i[1]) == None or type(i[1]) == str or i[1] != i[1]) and (type(i[2]) != None and i[2] == i[2])):
                                                if ("net sales" in i[0].lower() or "total revenue" in i[0].lower()):
                                                        if ("total" in i[0].lower()):
                                                                net_sales = [i[2]]
                                                                NS_page = 1
                                                        else:
                                                                net_sales.append(i[2])
                                                                NS_page = 1
                                                elif (("sales" in i[0].lower() or "revenue" in i[0].lower()) and len(net_sales)==0):
                                                        net_sales.append(i[2])
                                                        NS_page = 1
                                                elif ("total net sales" in i[0].lower()):
                                                        net_sales = [i[2]] # OVERWRITE
                                                        NS_page = 1                                                        
                                                elif (("net" in i[0].lower()) and ("loss" in i[0].lower() or "income" in i[0].lower() or "gain" in i[0].lower()) and ("tax" not in i[0].lower() and "discontinued" not in i[0].lower() and "share" not in i[0].lower() and "attributable" not in i[0].lower() and "other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                        net_income.append(i[2]) # OVERWRITE   
                                                        NI_page = 2
                                        elif (type(i[1]) != None and type(i[1]) != str and (i[1] == i[1])):
                                                if ("net sales" in i[0].lower() or "total revenue" in i[0].lower()):
                                                        if ("total" in i[0].lower()):
                                                                net_sales = [i[1]]
                                                                NS_page = 1
                                                        else:
                                                                net_sales.append(i[1])
                                                                NS_page = 1
                                                elif (("sales" in i[0].lower() or "revenue" in i[0].lower()) and len(net_sales)==0):
                                                        net_sales.append(i[1])   
                                                        NS_page = 1
                                                elif (("net" in i[0].lower()) and ("loss" in i[0].lower() or "income" in i[0].lower() or "gain" in i[0].lower()) and ("tax" not in i[0].lower() and "discontinued" not in i[0].lower() and "share" not in i[0].lower() and "attributable" not in i[0].lower() and "other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                        net_income.append(i[1])
                                                        NI_page = 2
        except:
                if (len(operations_sheet) > 1 and len(net_sales) == 0):
                        for i in dfs[operations_sheet[1][0]].values:
                                if (type(i[0]) is str):
                                        if (type(i[1]) != None and type(i[1]) != str and (i[1] == i[1])):
                                                if ("net sales" in i[0].lower() or "total revenue" in i[0].lower()):
                                                        if ("total" in i[0].lower()):
                                                                net_sales = [i[1]]
                                                                NS_page = 1
                                                        else:
                                                                net_sales.append(i[1])
                                                                NS_page = 1
                                                elif (("sales" in i[0].lower() or "revenue" in i[0].lower()) and len(net_sales)==0):
                                                        net_sales.append(i[1])   
                                                        NS_page = 1
                                                elif (("net" in i[0].lower()) and ("loss" in i[0].lower() or "income" in i[0].lower() or "gain" in i[0].lower()) and ("tax" not in i[0].lower() and "discontinued" not in i[0].lower() and "share" not in i[0].lower() and "attributable" not in i[0].lower() and "other" not in i[0].lower()) and ("miscellaneous" not in i[0].lower())):
                                                        net_income.append(i[1])
                                                        NI_page = 2
        
        try:
                for i in dfs[entity_sheet[0][0]].values:
                        if (type(i[0]) is str):
                                if ((type(i[1]) == None or type(i[1]) == str or i[1] != i[1]) and (type(i[2]) != None and i[2] == i[2])):
                                        if ("common" in i[0].lower() and "outstanding" in i[0].lower()):
                                                shares_outstanding = [i[2]]
                                                SO_page = 2
                                elif (type(i[1]) != None and type(i[1]) != str and (i[1] == i[1])):
                                        if ("common" in i[0].lower() and "outstanding" in i[0].lower()):
                                                shares_outstanding = [i[1]]
                                                SO_page = 2                                                
        except:
                if (len(entity_sheet) != 0):
                        for i in dfs[entity_sheet[0][0]].values:
                                if (type(i[0]) is str):
                                        if (type(i[1]) != None and type(i[1]) != str and (i[1] == i[1])):
                                                if ("common" in i[0].lower() and "outstanding" in i[0].lower()):
                                                        shares_outstanding = [i[1]]
                                                        SO_on_first_page = True 
                                                        SO_page = 2
               
        # TAKE FIRST VALUE OF ALL NUMBERS --> (correct value)
        
        # Balance Sheet Data
        if (len(current_assets) != 0):
                if ((type(current_assets[0]) == int or type(current_assets[0]) == float) and current_assets[0] == current_assets[0]):
                        current_assets = int(current_assets[0] * balance_sheet[0][1])
                else:
                        current_assets = -1
        else:
                current_assets = -1
                
        if (len(current_liabilities) != 0):
                if ((type(current_liabilities[0]) == int or type(current_liabilities[0]) == float) and current_liabilities[0] == current_liabilities[0]):
                        current_liabilities = int(current_liabilities[0] * balance_sheet[0][1])
                else:
                        current_liabilities = -1
        else:
                current_liabilities = -1
        
        if (len(total_assets) != 0):
                if ((type(total_assets[0]) == int or type(total_assets[0]) == float) and total_assets[0] == total_assets[0]):
                        total_assets = int(total_assets[0] * balance_sheet[0][1])
                else:
                        total_assets = -1
        else:
                total_assets = -1
        
        if (len(shares_outstanding) != 0):
                if (type(shares_outstanding[0]) == int or type(shares_outstanding[0]) == float and shares_outstanding[0] == shares_outstanding[0]):
                        if (SO_page == 0):
                                shares_outstanding = int(shares_outstanding[0] * balance_sheet[0][1])
                        elif (SO_page == 1):
                                shares_outstanding = int(shares_outstanding[0] * balance_sheet[1][1])
                        elif (SO_page == 2):
                                shares_outstanding = int(shares_outstanding[0] * entity_sheet[0][2])
                else:
                        shares_outstanding = -1
        else:
                shares_oustanding = -1
                
        if (len(preferred_outstanding) != 0):
                if ((type(preferred_outstanding[0]) == int or type(preferred_outstanding[0]) == float) and preferred_outstanding[0] == preferred_outstanding[0]):
                        if (PO_page == 0):
                                preferred_outstanding = int(preferred_outstanding[0] * balance_sheet[0][1])
                        elif (PO_page == 1):
                                preferred_outstanding = int(preferred_outstanding[0] * balance_sheet[1][1])
                else:
                        preferred_outstanding = -1
        else:
                preferred_outstanding = -1
        
        if (len(total_shareholder_equity) != 0):
                if ((type(total_shareholder_equity[0]) == int or type(total_shareholder_equity[0]) == float) and total_shareholder_equity[0] == total_shareholder_equity[0]):
                        total_shareholder_equity = int(total_shareholder_equity[0] * balance_sheet[0][1])
                else:
                        total_sharholder_equity = -1
        else:
                total_shareholder_equity = -1
        
        # Cash Sheet Data
        if (len(net_income) != 0):
                if ((type(net_income[0]) == int or type(net_income[0]) == float) and net_income[0] == net_income[0]):
                        if (NI_page == 0):
                                net_income = int(net_income[0] * cash_sheet[0][1])
                        elif (NI_page == 1):
                                net_income = int(net_income[0] * operations_sheet[0][1])
                        elif (NI_page == 2):
                                net_income = int(net_income[0] * operations_sheet[1][1])
                else:
                        net_income = -1
        else:
                net_income = 0
                
        if (len(cash_beg) != 0):
                if ((type(cash_beg[0]) == int or type(cash_beg[0]) == float) and cash_beg[0] == cash_beg[0]):
                        cash_beg = int(cash_beg[0] * cash_sheet[0][1])
                else:
                        cash_beg = -1
        else:
                cash_beg = -1
                
        if (len(cash_end) != 0):
                if ((type(cash_end[0]) == int or type(cash_end[0]) == float) and cash_end[0] == cash_end[0]):
                        cash_end = int(cash_end[0] * cash_sheet[0][1])
                else:
                        cash_end = -1
        else:
                cash_end = -1
        
        # Operations Sheet Data
        if (len(net_sales) != 0):
                if ((type(net_sales[0]) == int or type(net_sales[0]) == float) and net_sales[0] == net_sales[0]):
                        if (NS_page == 0):
                                net_sales = int(net_sales[0] * operations_sheet[0][1])
                        elif (NS_page == 1 and len(net_sales) != 0):
                                net_sales = int(net_sales[0] * operations_sheet[1][1])
                else:
                        net_sales = -1
        else:
                net_sales = -1
        

        ratios = {"symbols": symbol, "date":date, "net income": net_income, "current ratio": current_ratio, "PPS": PPS, "EPS": EPS, "asset turnover": asset_turnover, "PE ratio": PE_ratio, "cash flow": cash_flow, "return_on_equity": return_on_equity, "working_capital": working_capital} 
        
        
        # balance_data = [current_assets, current_liabilities, total_assets, shares_outstanding, preferred_outstanding, total_shareholder_equity]
        # cash_data = [net_income, cash_end, cash_beg]
        # operations_data = [net_sales]
        
        #
        #return [[balance_data],[cash_data],[operations_data]]
        
        
        values = {"symbols": symbol, "date":date, "current assets": current_assets, "current liabilities": current_liabilities, "total assets": total_assets, "shares outstanding": shares_outstanding, "preferred outstanding": preferred_outstanding, "total shareholder equity": total_shareholder_equity, "net income": net_income, "cash end": cash_end, "cash beg": cash_beg, "net sales": net_sales}
        
        return values

def get_ratios(values):
        # ======= RATIOS =======
        
        # current ratio = current assets / current liability
        # PPS = price of stock at day of release of report
        # EPS = (net income - preferred outstanding)/shares outstanding
        # asset turnover = net sales / total assets
        # PE ratio = PPS / EPS
        # cash flow = cash end - cash beg
        # return on equity = net income / total shareholder equity
        # working capital = current assets - current liabilities 
        
        # ======= Calculating =======
        try:
                current_ratio = values["current assets"] / values["current liabilities"]
        except:
                current_ratio = 0     
        try:
                PPS = get_pps(values["symbols"], values["date"]) 
        except:
                PPS = 0
        try:
                EPS = (values["net income"] - values["preferred outstanding"])/values["shares outstanding"]
        except:
                EPS = 0
        try:
                asset_turnover = values["net sales"] / values["total assets"]
        except:
                asset_turnover = 0
        try:
                PE_ratio = PPS / EPS
        except:
                PE_ratio = 0
        try:
                cash_flow = values["cash end"] - values["cash beg"]
        except:
                cash_flow = 0
        try:
                return_on_equity = values["net income"] / values["total shareholder equity"]
        except:
                return_on_equity = 0
        try:
                working_capital = values["current assets"] - values["current liabilities"]      
        except:
                working_capital = 0 
                
        ratios = {"symbol": values["symbols"], "date": values["date"], "current ratio": current_ratio, "PPS": PPS, "EPS": EPS, "asset turnover": asset_turnover, "PE ratio": PE_ratio, "cash flow": cash_flow, "return on equity": return_on_equity, "working capital": working_capital}       
        
        return ratios

def get_pps(symbol, date):
        file = "Price_Json_File\price_" + symbol + ".json"
        with open(file) as json_file:  
                data = json.load(json_file)
        '''
        if (date_curr not in data):
                while (date_curr not in data):
                        date_curr = date[8:] + ' '  + date[5:7] + ' ' + date[:4]
                        date_prev = str(datetime.datetime.strptime(date_curr, '%d %m %Y') + timedelta(days = -1))[:10]
                        date_curr = date_prev
        '''
        price = data[date]
        return price

# ===================================
# ======== Write to Database ========
# ===================================

def to_database(all_data):
        f = open( 'data_ratios.txt', 'w' )             # Use .txt file for now
        for i in all_data:
                f.write(str(i) + "\n")
        f.close()
        return True

def read_from_database():                       # Take in raw .txt file, and convert to dictionary
        with open("data_ratios.txt") as f:
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary
        return data

# ==============================================================
# ========================= DEBUGGING ==========================
# ==============================================================

def debug(all_data):                    # Print all company files' relevant data when encountering 
        hit = 0                         # a number under 10k (exclude preferred outstanding)
        for company in all_data:       
                for val in company:
                        if ("preferred outstanding" not in val and "symbols" not in val and "date" not in val):
                                if (type(company[val]) is int):
                                        if (abs(company[val]) < 10000 or abs(company[val]) > 100000000000):
                                                print(company)
                                                hit = hit + 1
                                                continue
                                else:
                                        print(company)
                                        hit = hit + 1
        if (hit == 0):
                print("No possibly incorrect data")
        return True

# =============================================================
# ======================= SPECIAL NOTES =======================
# =============================================================

# Some values where manually inserted, thus re-running the code WILL create bad data points

# ==== TO BE EXCLUDED ====
# GMO --> No net sales
# NG  --> No net sales
# TMQ --> No net sales
# UEC --> No net sales
# VGZ --> No net sales
# WWR --> No net sales
# XPL --> No net sales
# LEN --> No current assets/liabilities??

# all_data = extract_data() 
# debug(all_data)
# to_database(all_data)

ratios = []
loaded_data = read_from_database()
for i in loaded_data:
        ratios.append(get_ratios(i))
        print(ratios[-1])
to_database(ratios)