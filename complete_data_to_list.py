import json
import ast

def read_from_database():                                       # Take in raw str, and convert to dictionary
        with open("data_list_complete.json") as f:
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary

        data = data[0]                                          # Get database data as dictionary (rather than 1 item list)

        list_companies = data["2019-07-17"].keys()              # Company names
        list_companies.sort(reverse = False)                    # Sort alphabetically company names

        list_days = data.keys()                                 # Get Database days
        list_days = sorted(list_days, key = sorting)            # Sort days in past -> future order
                
        bad_companies = ["WLKP", "VMC", "VRS", "REX"]
        bad_days = []

        for day in list_days:
                num_companies = len(data[day])
                for company in list_companies:
                        if (company in bad_companies and company in data[day]):
                                del data[day][company]
                        if (num_companies < 161):
                                del data[day]
                                bad_days.append(day)
                                break

        for company in bad_companies:
                list_companies.remove(company)

        for day in bad_days:
                list_days.remove(day)

        # Give AGX data for April 14th (accidentally omitted)
        data["2016-04-14"]["AGX"] = data["2016-04-15"]["AGX"]


        num_days = len(data)
        num_companies = len(data["2016-04-14"])
        num_data_points = len(data["2016-04-14"]["AGX"])


        list_data = [[[0 for i in range(num_data_points)] for j in range(num_companies)] for k in range(num_days)]

        counter_i = 0
        counter_j = 0
        counter_k = 0
        for day in list_days:
                for company in list_companies:
                        for data_point in range(0,8):
                                list_data[counter_i][counter_j][counter_k] = data[day][company][data_point]
                                counter_k += 1
                        counter_k = 0
                        counter_j += 1
                counter_j = 0
                counter_i += 1

        return list_data

def sorting(L):
        splitup = L.split('-')
        return splitup[0], splitup[1], splitup[2]


list_data = read_from_database()


# FINAL LIST IS THE VARIABLE: list_data