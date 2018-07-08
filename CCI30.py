import csv
import math
import pandas as pd


def get_rates():
    cols = [0, 1, 2, 3, 4]
    metrics = pd.read_csv("CCI30/CCI30.csv", usecols=cols)
    return metrics

def index_values(assetCSV):
    values = get_rates()

    csv_index = open("CCI30/CCI30.csv")


if __name__ == '__main__':
    vals = get_rates()
    print(vals)
