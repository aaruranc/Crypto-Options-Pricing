import csv
import math
import pandas as pd

def get_rates():
    cols = [1, 2, 3, 4, 5]
    rates = pd.read_csv("risk_free_rates.csv", usecols=cols)
    return rates


def parse_rates(rates):
    parsed_rates = []
    last_rate = None
    for rate in rates:
        if math.isnan(rate):
            continue
        else:
            last_rate = rate
        parsed_rates.append(last_rate)
    return parsed_rates

def interest_rates(assetCSV):
    rates = get_rates()
    csv_file = open(assetCSV)
    r = csv.reader(csv_file)
    row0 = next(r)
    row0.append("T-Bill 1 Month")
    row0.append("T-Bill 3 Month")
    row0.append("T-Bill 6 Month")
    row0.append("T-Bill 1 Year")
    row0.append("T-Bill 2 Year")
    rows_to_write = [row0]

    count = 0
    weekday = count
    numskips = 0
    for row in r:
        skipped = 2 * numskips
        if weekday == 5:
            tempcount = count - skipped - 1
            weekday = weekday + 1
        elif weekday == 6:
            tempcount = count - skipped - 2
            weekday = 0
            numskips = numskips + 1
        else:
            tempcount = count - skipped
            weekday = weekday + 1
        row.append(rates["Treasury_Bill_1_Month"][tempcount])
        row.append(rates["Treasury_Bill_3_Month"][tempcount])
        row.append(rates["Treasury_Bill_6_Month"][tempcount])
        row.append(rates["Treasury_Bill_1_Year"][tempcount])
        row.append(rates["Treasury_Bill_2_Year"][tempcount])
        count = count + 1
        rows_to_write.append(row)
    out = open(assetCSV, 'w')
    csv_out = csv.writer(out)
    csv_out.writerows(rows_to_write)