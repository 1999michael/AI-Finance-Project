import ast

filename = "data_list_complete.json"
with open(filename) as f:              # *******FILE LOCATION/NAME MAY DIFFER ACCORDING TO YOUR REQUIREMENTS******
    content = f.readlines()
content = [x.strip() for x in content] 
data = []
for i in range(0,len(content)):
    data.append(ast.literal_eval(content[i]))       # Converting to dictionary

data = data[0]
count_zeros = 0
for i in data:
    for j in data[i]:
        for k in data[i][j]:
            if (k == 0.0 or k == 0 or k == -0.0):
                count_zeros += 1
print(count_zeros)