from pathlib import Path
import pandas as pd
import json
from math import ceil
import numpy as np
from module_2 import option_label


def price_JSON(current_directory):

    current_file = Path(current_directory) / 'historical.csv'
    df = pd.read_csv(current_file)

    a = []
    for index, series in df.iterrows():
        a.append({df['Date'][index]: df['Price'][index]})

    length = len(a)
    data = {'length': length, 'type': 'Price', 'data': a}
    x = json.JSONEncoder().encode(data)
    return x


def probability_density_JSON(df, method):

    payoff = method + '-P'
    payoff_df = df(columns=['Date', payoff]).copy()
    sorted_df = payoff_df.sort_values(by=[payoff])
    sorted_df.reset_index(drop=True)

    size = len(sorted_df)
    first_quartile = size // 4
    third_quartile = (size // 4) * 3
    IQR = third_quartile - first_quartile

    # Freedman-Diaconis Rule
    bin_width = (1 / np.cbrt(size)) * 2 * IQR

    count = 0
    bin_count = 1
    b = []
    for index, series in sorted_df.iterrows():
        if sorted_df[payoff][index] > (bin_count * bin_width):
            b.append({(bin_count * bin_width): count})
            count = 0
            bin_count = bin_count + 1
            continue
        count = count + 1

    num_bins = len(b)
    d = {'bins': num_bins, 'width': bin_width, 'data': b}
    return d


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

def query_JSON(query):

    trading_strategy = query['trading_strategy']
    length = query['option_length']
    strike = query['strike']
    current_directory = query['current_directory']

    method = str(strike) + '-' + trading_strategy
    option_length = option_label(length)
    rf_rates = option_length + '-LIBOR'
    rf_header = LIBOR_label(option_length)
    returns = method + '-ROI'

    current_file = Path(current_directory) / 'historical.csv'
    df = pd.read_csv(current_file)

    pdf = probability_density_JSON(df, method)

    a = []
    for index, series in df.iterrows():
        k = {'Price': df['Price'][index], 'Vol-Mean': df['Vol-Mean'][index], 'Vol-No-Mean': df['Vol-No-Mean'][index],
             'Strategy-Cost': df[method][index], rf_header: df[rf_rates][index], 'ROI': df[returns][index],
             'Probability-Density': pdf}
        p = {df['Date'][index]: k}
        a.append(p)

    df_length = len(a)
    d = {'length': df_length, 'type': 'Query', 'data': a}
    y = json.JSONEncoder().encode(d)
    return y


if __name__ == '__main__':
    print('main executed')
