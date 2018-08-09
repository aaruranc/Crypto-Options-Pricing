from pathlib import Path
import os
import pandas as pd
import strategies as strat
from math import sqrt, log

def handle_strategy(directory, length, current_file, df, strike, strategy):

    name = strategy[:-2]
    method = str(strike) + '-' + strategy
    payoff = method + '-P'
    ROI = method + '-ROI'

    if strategy == 'Calls':
        return
    elif strategy == 'Puts':
        return
    elif strategy == 'Straddles':
        strat.straddle(current_file, df, method, payoff, ROI)
        return
    elif name == 'Bear-Spreads':
        strat.bear_spreads(directory, length, current_file, df, strike, strategy, method, payoff, ROI)
        return

    ##### Add the rest of the strategies

    return

def call_price()


def BS_dict(df, index, length, percentage):

    d = {'strike': '', 'spot': '', 'rf': '', 'd1_mean': 0, 'd2_mean': 0, 'd1_no_mean': 0, 'd2_no_mean': 0,
         'length': length}

    if (length + 3) > index:
        return d

    spot = df['Price'][index]
    ratio = percentage / 100
    strike = spot * ratio
    d.update({'strike': strike, 'spot': spot})

    title = option_label(length)
    v_m = title + '-VM'
    v_nm = title + '-VNM'
    rf_title = title + '-LIBOR'
    rf = df[rf_title][index]
    vol_mean = df[v_m][index]
    vol_no_mean = df[v_nm][index]

    d1_mean = (1 / (vol_mean * sqrt(length))) * (log((1 / ratio)) + (rf + ((vol_mean ** 2) / 2)) * length)
    d2_mean = d1_mean - vol_mean * sqrt(length)
    d1_no_mean = (1 / (vol_no_mean * sqrt(length))) * (log((1 / ratio)) + (rf + ((vol_no_mean ** 2) / 2)) * length)
    d2_no_mean = d1_no_mean - vol_no_mean * sqrt(length)

    d.update({'rf': rf, 'd1_mean': d1_mean, 'd2_mean': d2_mean, 'd1_no_mean': d1_no_mean, 'd2_no_mean': d2_no_mean})
    return d


def new_strike_data(query_file, df, length, strike):

    title = str(strike)
    c = title + '-Calls'
    p = title + '-Puts'

    percentage = strike / 100
    strike_df = pd.DataFrame(columns=['Price']).copy()
    strike_df.rename(columns={'Price': title})
    strike_df.applymap(lambda x: x * percentage)

    headers = [(c + '-VM'), (c + '-VM-P'), (c + '-VM-ROI'), (c + '-VNM'), (c + '-VNM-P'), (c + '-VNM-ROI'),
               (p + '-VM'), (p + '-VM-P'), (p + '-VM-ROI'), (p + '-VNM'), (p + '-VNM-P'), (p + '-VNM-ROI')]
    options_df = pd.DataFrame(columns=headers)
    d = {}
    size = len(df)

    for index, series in df.iterrows():
        if size < (index + length + 1):
            break

        BS_data = BS_dict(df, index, length, percentage)

        d.update({(c + '-VM'): call_price(BS_data),
                  (c + '-VM-P'): 0,
                  (c + '-VM-ROI'): 0,
                  (c + '-VNM'): call_price(BS_data),
                  (c + '-VNM-P'): 0,
                  (c + '-VNM-ROI'): 0,
                  (p + '-VM'): put_price(BS_data),
                  (p + '-VM-P'): 0,
                  (p + '-VM-ROI'): 0,
                  (p + '-VNM'): put_price(BS_data),
                  (p + '-VNM-P'): 0,
                  (p + '-VNM-ROI'): 0,
                  })
        options_df.append(d, ignore_index=True)
    updated_df = pd.concat([df, strike_df, options_df], axis=1)
    updated_df.to_csv(query_file)
    return


def option_label(length):

    if length <= 14:
        option_length = str(length) + '-Day'
    elif 14 < length < 365:
        num = length // 30
        option_length = str(num) + '-Month'
    else:
        option_length = '1-Year'
    return option_length


def search_and_compute(query):

    trading_strategy = query['trading_strategy']
    length = query['option_length']
    strike = query['strike']
    current_directory = query['current_directory']

    option_length = option_label(length)

    loc = option_length + '.csv'
    query_directory = Path(current_directory) / option_length
    query_file = query_directory / loc

    if os.path.isdir(query_directory):
        df = pd.read_csv(query_file)
        headers = list(df)
        strike_str = str(strike)
        if strike_str in headers:
            method = strike_str + '-' + trading_strategy
            if method in headers:
                return
            else:
                handle_strategy(current_directory, length, query_file, df, strike, trading_strategy)
                return

        else:
            new_strike_data(query_file, df, length, strike)
            handle_strategy(current_directory, length, query_file, df, strike, trading_strategy)
            return

    else:
        os.mkdir(query_directory)
        df = 0
        # Create Directory
        # Create File
        # Append Data (up to Call/Put Payoffs)
        handle_strategy(current_directory, length, query_file, df, strike, trading_strategy)
        return


if __name__ == '__main__':
    return