import csv
import math
import pandas as pd


def get_rates(assetCSV):
    metrics = pd.read_csv("CCI30/CCI30.csv")
    return metrics

def index_values(assetCSV):
    csv_index = open("CCI30/CCI30.csv")

