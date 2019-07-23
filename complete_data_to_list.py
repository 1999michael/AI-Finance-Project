import json
import ast

def read_from_database():                       # Take in raw .txt file, and convert to dictionary
        with open("data_list_complete.json") as f:
                content = f.readlines()
        content = [x.strip() for x in content] 
        data = []
        for i in range(0,len(content)):
                data.append(ast.literal_eval(content[i]))       # Converting to dictionary
        return data

data = read_from_database()[0]
data_dict = data
company_names = data["2019-06-06"]
company_names = company_names.keys()
print(company_names)
#print(data)
company_names_test = data["2016-01-06"]
company_names_test = company_names_test.keys()
print(company_names_test)

data = data.keys()
data.sort() # Days 

num_days = 891
num_companies = 119 # any day works
num_data_points = 8 # any company works

print(data)

list_data = [[[0 for i in range(num_data_points)] for j in range(num_companies)] for k in range(num_days)]

print(len(list_data))
print(len(list_data[0]))
print(len(list_data[0][0]))

counter_i = 0
counter_j = 0
counter_k = 0
for day in data:
        for company in company_names:
                for data_point in range(0,8):
                        list_data[counter_i][counter_j][counter_k] = data_dict[day][company][data_point]
                        counter_k += 1
                counter_k = 0
                counter_j += 1
        counter_j = 0
        counter_i += 1

print(list_data)
#print(list_data)
