import datetime
import csv
import sys
import pandas as pd

def get_info(asset):
    cols = [0, 1]
    info = pd.read_csv(asset, usecols=cols)
    return info

def dateTime(asset):
    info = get_info(asset)
    # print(info)
    updated_info = []

    HARDCODE = "str"

    count = 0
    for row in info:
        if count == 7:
            break

        date = info['Date'][count]
        print(date)

        datetime.

        strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')

        count = count + 1
    # out = open(assetCSV, 'w')
    # csv_out = csv.writer(out)
    # csv_out.writerows(rows_to_write)


if __name__ == '__main__':
    dateTime('test.csv')
