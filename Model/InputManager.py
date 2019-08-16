import os
import json
from ast import literal_eval
import pandas as pd
import numpy as np
from datetime import datetime as dt
import statistics

class InputManager:
    def __init__(self):
        self.dataFileLocation = os.path.join(os.getcwd(),'data_ratios.txt')
        self.incompleteDF = None
        self.date_ordered_json_list = None

    def transferToJson(self):
        '''
        'data_list_incomplete.json' will be the json file include the future input that only contains certain
        dates(when the financial statement is released for each company, )
        '''
        # get the date for each company that their financial statement came out
        jsonPath = os.path.join(os.getcwd(), 'data_list_incomplete.json')

        with open(self.dataFileLocation, 'r') as dataFile:
            with open(jsonPath, 'w') as jsonFile:
                for lines in dataFile:
                    line = literal_eval(lines)
                    json.dump(line, jsonFile)
                    jsonFile.write('\n')
        self.incompleteDF = pd.read_json(jsonPath, lines = True) # lines = True --> Read the file as a json object per line.

        # Change json file to csv file to be used for dataframe

    def getJson(self):
        jsonPath = os.path.join(os.getcwd(), 'data_list.json')

        companyList = self.incompleteDF.symbol.unique()
        col_name = list(self.incompleteDF.columns)

        # Move the position of pps to the end of the list
        col_name.remove('date')
        col_name.remove('symbol')

        date_ordered_json_list = {}

        for company in companyList:
            date_ordered_json_list[company] = {}
            lineNums = np.where(self.incompleteDF.symbol == company)[0]

            for lineNum in lineNums:
                date = self.incompleteDF.iloc[lineNum]['date']
                date = str(date)[0:10]
                value_list = [float(self.incompleteDF.iloc[lineNum][col]) for col in col_name]
                 # ['EPS', 'PE ratio','PPS',  'asset turnover', 'cash flow', 'current ratio', 'return on equity', 'working capital']
                date_ordered_json_list[company][date] = value_list

            with open(jsonPath, 'w') as fp:
                json.dump(date_ordered_json_list, fp)
                fp.write('\n')

        self.date_ordered_json_list = date_ordered_json_list
        return

    def makeDuplicates(self):
        '''
        Since before we only have ['EPS', 'PE ratio', 'PPS', 'asset turnover', 'cash flow', 'current ratio',
        'return on equity', 'working capital', closePrice, the14DayAverage, the37DayAverage] for the date that the company released their financial statement
        In here, we make the full list of every trading day in the past 3 years
        :return:
        '''

        # Get company info (8 inputs) to json file
        self.getJson()
        dir_name = os.path.join(os.getcwd(), 'StockDataCSVFile')
        jsonPath = os.path.join(os.getcwd(), 'data_list_complete.json')
        firstfinstatementList = []

        for company in list(self.date_ordered_json_list.keys()):
            finDate = list(self.date_ordered_json_list[company].keys())

            #get each company's stock data
            file_name = '{}_Data.csv'.format(company)
            companyCSVPath = os.path.join(dir_name, file_name)
            dfComplete = pd.read_csv(companyCSVPath)

            # get line number in the panda
            finDateLines = []
            for i in finDate:
                dateLine = (np.where(dfComplete.Date == i)[0]).tolist()
                if dateLine != []:
                    finDateLines += dateLine
            firstfinstatementList.append(finDate[0])

            for i in range(len(finDateLines)):
                start = finDateLines[i]
                if i != len(finDateLines) - 1:
                    end = finDateLines[i+1]
                else:
                    end = -1

                self.updateDataJsonList(start, end, dfComplete, company)
        firstfinstatementList.sort()


        self.date_ordered_json_list = self.changeFormat()

        fristdate = dt.strptime(firstfinstatementList[-1], "%Y-%m-%d")

        for date in list(self.date_ordered_json_list.keys()):
            curDate = dt.strptime(date, "%Y-%m-%d")
            if curDate < fristdate:
                del self.date_ordered_json_list[date]

        with open(jsonPath, 'w') as fp:
            json.dump(self.date_ordered_json_list, fp)
            fp.write('\n')

    def updateDataJsonList(self,start,end, dfComplete, company):
        '''
        Complete the input list that will be used for future normalization and change into tensor to include stock price information
        :param start: the date that financial statement info will be duplicate
        :param end: the last date the above financial statement info will be used to duplicate
        '''

        dataInBetween = dfComplete.iloc[start:end]

        closingPriceInBetween = list(dataInBetween['Close'])
        dateInBetween = list(dataInBetween['Date'])
        inBetweenList = zip(closingPriceInBetween, dateInBetween)

        finDataValues = self.date_ordered_json_list[company][dateInBetween[0]]

        # Update company financial statement data to include stock price data
        for (i,(closePrice, date)) in enumerate(inBetweenList):
            # Calculate 14 days moving average
            #print(dfComplete)
            first14DayData = dfComplete.iloc[(start+i-14):(start+i)]
            first14DayClose = list(first14DayData['Close'])
            the14DayAverage = statistics.mean(first14DayClose)

            # Calculating 37 days moving average
            first37DayData = dfComplete.iloc[(start + i - 37):(start + i)]
            first37DayClose = list(first37DayData['Close'])
            the37DayAverage = statistics.mean(first37DayClose)

            new = finDataValues + [closePrice] + [the14DayAverage] + [the37DayAverage]

            # update 14 days variable and 37 days variable
            self.date_ordered_json_list[company][date] = new

    def changeFormat(self):
        '''
        Change from {company:{date:[value list]}} to {date:{company:[value list]}} to make generating input easier
        '''
        f_Format = {}
        for company in self.date_ordered_json_list:
            for date in self.date_ordered_json_list[company]:
                if date in f_Format:
                    f_Format[date][company] = self.date_ordered_json_list[company][date]
                else:
                    f_Format[date] = {}
                    f_Format[date][company] = self.date_ordered_json_list[company][date]

        return f_Format










