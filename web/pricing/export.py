from pathlib import Path
import pandas as pd
import json
import time
import numpy as np
from scipy import stats


def update_query(query, session):
    query.update({'current_directory': session['location'], 'source': session['source'],
                  'trading_days': session['trading_days']})
    return query


def price_JSON(current_file):

    df = pd.read_csv(current_file)

    b = []
    for index, series in df.iterrows():
        a = []
        a.append(int(df['Timestamp'][index]))
        a.append(df['Price'][index])
        b.append(a)

    data = json.dumps(b)
    # y = json.JSONEncoder().encode(b)
    return data


def LIBOR_label(rf_rates):

    if rf_rates == '1-Day':
        return '1-Day-LIBOR'
    elif rf_rates == '1-Week':
        return '1-Week-LIBOR'
    elif rf_rates == '1-Month':
        return '1-Month-LIBOR'
    elif rf_rates == '2-Month':
        return '2-Month-LIBOR'
    elif rf_rates == '3-Month':
        return '3-Month-LIBOR'
    elif rf_rates == '6-Month':
        return '6-Month-LIBOR'
    elif rf_rates == '1-Year':
        return '1-Year-LIBOR'
    else:
        return 'Synthetic LIBOR'

def option_label(length):
    
    if length <= 14:
        option_length = str(length) + '-Day'
    elif 14 < length < 365:
        num = length // 30
        option_length = str(num) + '-Month'
    else:
        option_length = '1-Year'
    return option_length


def UNIX_timestamp(val):
    x = int(time.mktime(val.timetuple()))*1000
    return x


def query_JSON(query):

    trading_strategy = query['trading_strategy']
    length = int(query['option_length'])
    strike = int(query['strike'])
    request = query['request']
    current_directory = Path(query['current_directory'])
    source = Path(query['source'])
    trading_days = query['trading_days']

    method = str(strike) + '-' + trading_strategy
    payoff = method + '-P'
    returns = method + '-ROI'

    option_length = option_label(length)
    rf_rates = option_length + '-LIBOR'
    rf_header = LIBOR_label(option_length)
    vol = option_length + '-VM'

    current_file = option_length + '.csv'
    file_loc = current_directory / current_file
    df = pd.read_csv(file_loc)
    df_length = len(df)

    if request == 'price':
        data = 'Price'
    elif request == 'volatility':
        data = vol
    elif request == 'strategy-cost':
        data = method
    elif request == 'payoff':
        data = payoff
    elif request == 'ROI':
        data = returns
    elif request == 'pdf':
        data = payoff


    k = []
    for index, series in df.iterrows():
        if index <= length:
            continue
        if (index + length) == df_length:
            break
        val = float(df[data][index])
        if np.isnan(val) or val > 9007199254740991:
            continue
        else:
            if request == 'pdf':
                j = [float("{0:.3f}".format(val)), int(df['Timestamp'][index])]
            else:
                j = [int(df['Timestamp'][index]), float("{0:.3f}".format(val))]
            k.append(j)

    if request == 'pdf':
        stat = stats.describe(df[data], nan_policy='omit')
        statistics = {'samples': int(stat[0]), 'min': float(stat[1][0]), 'max': float(stat[1][1]),
                      'mean': float(stat[2]), 'variance': float(stat[3]), 'skewness': float(stat[4]),
                      'kurtosis': float(stat[5])}
        d = {'data': k, 'stats': statistics}
        json_data = d

    else:
        json_data = k

    y = json.JSONEncoder().encode(json_data)
    return y


if __name__ == '__main__':

    test_query = {'trading_strategy': 'Calls', 'option_length': '2', 'strike': '122', 'request': 'pdf',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv',
                  'trading_days': 'weekdays-H'}
    print('export_data main executed')
    query_JSON(test_query)
