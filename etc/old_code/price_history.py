import pandas as pd
from collections import OrderedDict
from math import log, sqrt


def annualize(n):
    x = n * sqrt(365)
    return x


def calc_volatility(step_1, series, step):
    if step == 1:
        return 0

    s = 0
    for i in range((series - step), series):

        if i >= 1:
            log_return = log(step_1['Price'][i] / step_1['Price'][i-1])
        else:
            log_return = 0
        s = s + log_return

    mu = s / step
    total = 0

    for j in range((series - step), series):

        if j >= 1:
            diff = (log(step_1['Price'][j] / step_1['Price'][j-1]) - mu) ** 2
        else:
            diff = 0
        total = total + diff

    vol = annualize(sqrt(total / (step - 1)))
    return vol


def calc_volatility_no_mean(step_1, series, step):
    if step == 1:
        if series >= 1:
            log_return = log(step_1['Price'][series] / step_1['Price'][series - 1])
            return annualize(log_return ** 2)

    total = 0
    for j in range((series - step), series):
        if j >= step + 1:
            diff = (log(step_1['Price'][j] / step_1['Price'][j - 1])) ** 2
        else:
            diff = 0
        total = total + diff
    vol = annualize(sqrt(total / (step - 1)))
    return vol


def adjust_move(step_1, series, step):
    new_move = step_1['Price'][series] - step_1['Price'][series - step]
    return  new_move


def adjust_change(step_1, series, step):
    new_change = ((step_1['Price'][series] - step_1['Price'][series - step]) / step_1['Price'][series - step]) * 100
    return new_change


def moves_n_volatilities(step_1, date_dffs, header_tags, series):
    if series == 0:
        return

    a = []
    d = {}

    for step in date_dffs:
        if step < series + 1:
            a.append(adjust_move(step_1, series, step))
            a.append(adjust_change(step_1, series, step))
            a.append(calc_volatility(step_1, series, step))
            a.append(calc_volatility_no_mean(step_1, series, step))

    count = 0
    for val in a:
        d.update({header_tags[count]: val})
        count = count + 1
    return d


def price_movements(step_1, start):

    date_dffs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 30, 60, 90, 120, 150, 180, 365, 730]
    header_tags = []
    duration = ('Day', 'Month', 'Year')

    for length in date_dffs:

        w = 7
        y = 365
        if length <= 2 * w:
            label = duration[0]
        if 2 * w < length < y:
            length = length // 30
            label = duration[1]
        if length >= y:
            length = length // 365
            label = duration[2]

        move = str(length) + ' ' + str(label) + ' ' + 'Movement'
        change = str(length) + ' ' + str(label) + ' ' + 'Percent Change'
        vol_w_mean = str(length) + ' ' + str(label) + ' ' + 'Annualized Volatility w/ Mean'
        vol_w_o_mean = str(length) + ' ' + str(label) + ' ' + 'Annualized Volatility w/o Mean'
        header_tags.append(move)
        header_tags.append(change)
        header_tags.append(vol_w_mean)
        header_tags.append(vol_w_o_mean)

    headers = OrderedDict.fromkeys(header_tags, [''])
    df = pd.DataFrame.from_dict(headers)
    size = step_1.size
    q = size // 4
    h = size // 2
    t = (size * 3) // 4

    for series, index in step_1.iterrows():
        print(series)
        if series == q:
            print('25 % Done')
        if series == (h - 1) or series == h or series == (h + 1):
            print('50% Done')
        if series == (t - 1) or series == t or series == (t + 1):
            print('75% Done')
        if series == (size - 1):
            print('100% Done')

        df = df.append(moves_n_volatilities(step_1, date_dffs, header_tags, series), ignore_index=True)

    step_2 = pd.concat([step_1, df], axis=1)

    return(step_2)
