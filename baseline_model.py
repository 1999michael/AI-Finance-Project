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
from data_input_formatting import data_collect


# ========================================
# =============== Get Data ===============
# ========================================

# Data for a single company

data_single_company =  data_collect(normalize_function = 2, 
                                    normalize_company = 0, 
                                    num_range = 1,
                                    train_size = 70, 
                                    val_size = 15, 
                                    test_size = 15, 
                                    start_point_diff = 25, 
                                    start_point_deviation = 5, 
                                    length = 25, 
                                    pred_length = 5, 
                                    company_group = False, 
                                    random_batch = False, 
                                    no_change_range = 5, 
                                    data_points = range(0,11))

# True means get data from .json database. None means use random data
# can use, for example data_single_company.get_label_frequency(train_data_single, "Train") to print label frequencies (return True)
train_data_single, val_data_single, test_data_single = data_single_company.format_data(True) 

data_all_company = data_collect(normalize_function = 2, 
                                normalize_company = 0, 
                                num_range = 1,
                                train_size = 70, 
                                val_size = 15, 
                                test_size = 15, 
                                start_point_diff = 25, 
                                start_point_deviation = 5, 
                                length = 25, 
                                pred_length = 5, 
                                company_group = True, 
                                random_batch = False, 
                                no_change_range = 5, 
                                data_points = range(0,11))

train_data_all, val_data_all, test_data_all = data_all_company.format_data(True) 


# ======================================
# =============== Models ===============
# ======================================

class neuralnet_single_company(nn.Module):
    def __init__(self, data_points, length):
        super(neuralnet_single_company, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=7, kernel_size=3)
        self.fc1 = nn.Linear(7 * 11 * 9, 121)
        self.fc2 = nn.Linear(121, 15)
        self.fc3 = nn.Linear(15,1)
        self.length = length
        self.data_points = data_points
        
    def forward(self, x):
        x = x.view(-1, 1, self.length, self.data_points).cuda()
        x = F.selu(self.conv1(x)).cuda()
        x = x.view(-1, 7 * 11 * 9).cuda()
        x = F.selu(self.fc1(x)).cuda()
        x = F.relu(self.fc2(x)).cuda()
        x = self.fc3(x).cuda()
        return x

class neuralnet_single_company_simple(nn.Module):
    def __init__(self):
        super(neuralnet_single_company_simple, self).__init__()
        self.fc1 = nn.Linear(25 * 11, 10)
        self.fc2 = nn.Linear(10, 1)
        
    def forward(self, x):
        x = x.view(-1, 25 * 11).cuda()
        x = torch.tanh(self.fc1(x)).cuda()
        x = self.fc2(x).cuda()
        return x

class neuralnet_all_company(nn.Module):
    def __init__(self, num_data = 11, length = 25):
        super(neuralnet_all_company, self).__init__()
        self.fc1 = nn.Linear(num_data * length * 161, 3000)
        self.fc2 = nn.Linear(3000, 1000)
        self.fc3 = nn.Linear(1000, 300)
        self.fc4 = nn.Linear(300, 161)
        self.length = length
        self.num_data = num_data
        
    def forward(self, x):
        x = x.view(-1, self.num_data * self.length * 161)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x

# ===============================================================
# =============== Accuracy and training functions ===============
# ===============================================================

torch.manual_seed(1000) # set random seed

def train(model, train_data, val_data, batch_size=16, num_epochs=100, lr = 0.0001, no_change_range = 2.0, company_group = False):
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    iters, losses, val_losses, train_acc, val_acc = [], [], [], [], []
    
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size)
    val_loader = torch.utils.data.DataLoader(val_data, batch_size = batch_size)
    
    # training
    n = 0 
    for epoch in range(num_epochs):
        for data, labels in iter(train_loader):
            out = model(data).cuda()
            if (company_group == False):
                labels = labels.unsqueeze(1).float().cuda()
            loss = criterion(out, labels)
            loss.backward()             
            optimizer.step()              
            optimizer.zero_grad()
              

        # save training info
        iters.append(n)
        losses.append(float(loss)/batch_size) 
        
        for data, labels in iter(val_loader):
            out = model(data).cuda()
            labels = labels.unsqueeze(1).float().cuda()
            loss = criterion(out, labels)
        val_losses.append(float(loss)/batch_size)
        
        # Training and Validation Accuracy
        train_acc.append(get_accuracy(model, train_data, batch_size = batch_size, no_change_range = no_change_range))
        val_acc.append(get_accuracy(model, val_data, batch_size = batch_size, no_change_range = no_change_range))
        n += 1
        # Output Accuracy for each epoch
        print("Epoch: ",(epoch + 1), "    Train Loss: ", losses[n-1],"      Val Loss: ", val_losses[n-1],"    Train Accuracy: ", train_acc[n-1], "     Validation Accuracy: ", val_acc[n-1])

    # plotting
    plt.title("Training Curve")
    plt.plot(iters, losses, label="Train")
    plt.plot(iters, val_losses, label = "Val")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.legend(loc = 'best')
    plt.show()

    plt.title("Training Curve")
    plt.plot(iters, train_acc, label="Train")
    plt.plot(iters, val_acc, label="Validation")
    plt.xlabel("Iterations")
    plt.ylabel("Training Accuracy")
    plt.legend(loc='best')
    plt.show()

    print("Final Training Accuracy: {}".format(train_acc[-1]))
    print("Final Validation Accuracy: {}".format(val_acc[-1]))  

def get_accuracy(model, data, batch_size = 16, no_change_range = 2.0):
    data_loader = torch.utils.data.DataLoader(data, batch_size=batch_size)
    correct = 0
    total = 0
    for data, labels in data_loader:
        output = model(data).cuda() # Forward Pass
        labels = labels.view(-1,1).cuda()
        correct += compare_pred(labels, output, no_change_range)
        total += len(labels)
    return correct / total

def compare_pred(labels, pred, no_change_range):
    list_labels = labels.tolist()
    list_pred = pred.tolist()
    correct = 0
    for i in range(0,len(list_labels)):
      if (int(list_labels[i][0]) == -1 and list_pred[i][0] <= (-no_change_range/100.0)):
        correct += 1
      elif (int(list_labels[i][0]) == 0 and (list_pred[i][0] < (no_change_range/100.0) and list_pred[i][0] > (-no_change_range/100.0))):
        correct += 1
      elif (int(list_labels[i][0]) == 1 and list_pred[i][0] >= (no_change_range/100.0)):
        correct += 1
    return correct

# ==================================================
# ==================== Training ====================
# ==================================================

length = 25     # Number of days in a single item 
num_data = 11   # Number of data points we are using

# Training our model --> GENERIC MODEL

model = neuralnet_single_company(num_data, length).cuda()
train(model, train_data_single, val_data_single, batch_size=16, num_epochs=200, lr = 0.00002, company_group = False, no_change_range = 2.0)


#  Training our model --> ALL COMPANIES AT SAME TIME

model_all = neuralnet_all_company(num_data, length).cuda()
train(model_all, train_data_all, val_data_all, batch_size=16, num_epochs=200, lr = 0.00002, company_group = True, no_change_range = 2.0)