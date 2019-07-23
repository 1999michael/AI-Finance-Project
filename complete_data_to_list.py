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
print(len(data))
print(data["2016-03-01"])
print(data["2016-03-01"]["AEGN"])