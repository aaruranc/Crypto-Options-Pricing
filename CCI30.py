import csv
import math
import pandas as pd


def get_rates():
    cols = [0, 1, 2, 3, 4]
    metrics = pd.read_csv("CCI30/CCI30.csv", usecols=cols)
    return metrics

def index_values(assetCSV):
    metrics = get_rates()
    csv_file = open(assetCSV)
    r = csv.reader(csv_file)
    row0 = next(r)
    row0.append("CCI30 Open")
    row0.append("CCI30 High")
    row0.append("CCI30 Low")
    row0.append("CCI30 Close")
    rows_to_write = [row0]



if __name__ == '__main__':
    vals = get_rates()
    print(vals)
