import pandas as pd

def str_adjust(date, length):
    if length == 6:
        new_date = "0" + date[0:2] + "0" + date[2:]
        return  new_date
    if length == 7:
        if date[1] == "/":
            new_date = "0" + date
            return new_date
        else:
            new_date = date[0:3] + "0" + date[3:]
            return new_date

def start_date(assetCSV):
    cols = [0]
    info = pd.read_csv(assetCSV, usecols=cols)
    first = info['Date'][0]
    start = str_adjust(first, len(str(first)))
    return start

def standardize_date(assetCSV):
    cols = [0, 1]
    info = pd.read_csv(assetCSV, usecols=cols)
    for series, index in info.iterrows():
        date = info.at[series, 'Date']
        new_date = str_adjust(date, len(str(date)))
        info.at[series, 'Date'] = new_date
    return info

if __name__ == '__main__':
    standardize_date('test.csv')
