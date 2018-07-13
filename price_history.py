import pandas as pd
from collections import OrderedDict


def adjust_move(step_1, series, step):
    new_move = step_1['Price'][series] - step_1['Price'][series - step]
    return  new_move

def adjust_change(step_1, series, step):
    new_change = ((step_1['Price'][series] - step_1['Price'][series - step]) / step_1['Price'][series - step]) * 100
    return new_change

def moves_n_changes(step_1, date_diffs, header_tags, series):
    if series == 0:
        return
    adjustments = []
    dict = {}
    for step in date_diffs:
        if step < series + 1:
            adjustments.append(adjust_move(step_1, series, step))
            adjustments.append(adjust_change(step_1, series, step))
    count = 0
    for val in adjustments:
        dict.update({header_tags[count]: val})
        count = count + 1
    return dict

def price_movements(step_1):
    date_diffs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 30, 60, 90, 120, 150, 180, 365, 545, 730]
    header_tags = []
    for length in date_diffs:
        if length < 15:
            title = str(length) + ' ' + 'Day Movement'
            header_tags.append(title)
            title = str(length) + ' ' + 'Day Percent Change'
            header_tags.append(title)
        if 14 < length < 365:
            length = length // 30
            title  = str(length) + ' ' + 'Month Movement'
            header_tags.append(title)
            title = str(length) + ' ' + 'Month Percent Change'
            header_tags.append(title)
        if length == 365:
            title = '1 Year Movement'
            header_tags.append(title)
            title = '1 Year Percent Change'
            header_tags.append(title)
        if length == 545:
            title = '1.5 Year Movement'
            header_tags.append(title)
            title = '1.5 Year Percent Change'
            header_tags.append(title)
        if length == 730:
            title = '2 Year Movement'
            header_tags.append(title)
            title = '2 Year Percent Change'
            header_tags.append(title)

    headers = OrderedDict.fromkeys(header_tags, ['NaN'])
    df = pd.DataFrame.from_dict(headers)
    for series, index in step_1.iterrows():
        df = df.append(moves_n_changes(step_1, date_diffs, header_tags, series), ignore_index=True)
    step_2 = pd.concat([step_1, df], axis=1)
    return(step_2)

if __name__ == '__main__':
    asset = 'test.csv'
    price_movements(asset)