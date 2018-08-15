from pathlib import Path
import os
import pandas as pd
from math import sqrt, log
import strategies


def BS_option_calcs(parameters):

    return {}


def BS_dict(df, index, length, percentage):

    d = {'length': length}

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
    risk_free = df[rf_title][index]
    vol_mean = df[v_m][index]
    vol_no_mean = df[v_nm][index]

    compute_d1 = lambda v, l, r, rf : (1/(v*sqrt(l)))*(log((1/r))+(rf+((v**2)/2)*l))
    compute_d2 = lambda d1, v, l: d1-(v*sqrt(l))

    d1_mean = compute_d1(vol_mean, length, ratio, risk_free)
    d2_mean = compute_d2(d1_mean, vol_mean, length)
    d1_no_mean = compute_d1(vol_no_mean, length, ratio, risk_free)
    d2_no_mean = compute_d2(d1_no_mean, vol_no_mean, length)

    d.update({'d1_mean': d1_mean, 'd2_mean': d2_mean, 'd1_no_mean': d1_no_mean, 'd2_no_mean': d2_no_mean})
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

        parameters = BS_dict(df, index, length, percentage)
        data = BS_option_calcs(parameters)

        d.update({(c + '-VM'): data['Calls']['Mean']['Price'],
                  (c + '-VM-P'): data['Calls']['Mean']['Payoff'],
                  (c + '-VM-ROI'): data['Calls']['Mean']['ROI'],
                  (c + '-VNM'): data['Calls']['No-Mean']['Price'],
                  (c + '-VNM-P'): data['Calls']['No-Mean']['Payoff'],
                  (c + '-VNM-ROI'): data['Calls']['Mean']['ROI'],
                  (p + '-VM'): data['Puts']['Mean']['Price'],
                  (p + '-VM-P'): data['Puts']['Mean']['Payoff'],
                  (p + '-VM-ROI'): data['Puts']['Mean']['ROI'],
                  (p + '-VNM'): data['Puts']['No-Mean']['Price'],
                  (p + '-VNM-P'): data['Puts']['No-Mean']['Payoff'],
                  (p + '-VNM-ROI'): data['Puts']['Mean']['ROI'],
                  })
        options_df.append(d, ignore_index=True)
    updated_df = pd.concat([df, strike_df, options_df], axis=1)
    updated_df.to_csv(query_file)
    return


def handle_strategy(current_directory, current_file, df, length, strike, strategy):

    method = str(strike) + '-' + strategy

    if strategy == 'Calls':
        strategies.calls(current_file, df, length, strike)
        return
    elif strategy == 'Puts':
        strategies.puts()
        return
    elif strategy == 'Straddles':
        strategies.straddle(current_file, df, method)
        return
    elif strategy == 'Bear-Spreads':
        strategies.bear_spreads(current_directory, length, current_file, df, strike, strategy, method)
        return

    ##### Add the rest of the strategies

    return


# def calc_volatilities(df, option_length):
#     return []
#
#
# def grab_LIBOR(dates):
#     return []
#
#

def grab_dates(df):

    l = len(df)
    e = l - 1
    start_date = df['Date'][0]
    end_date = df['Date'][e]
    d = {'start': start_date, 'end': end_date}
    return d


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
    source = query['source']

    option_length = option_label(length)

    loc = option_length + '.csv'
    query_file = current_directory / loc

    if os.path.isfile(query_file):
        df = pd.read_csv(query_file)
        headers = list(df)
        strike_str = str(strike)
        if strike_str in headers:
            method = strike_str + '-' + trading_strategy
            if method in headers:
                return
            else:
                handle_strategy(current_directory, query_file, df, length, strike, trading_strategy)
                return

        else:
            new_strike_data(query_file, df, length, strike)
            handle_strategy(current_directory, query_file, df, length, strike, trading_strategy)
            return

    else:
        df = pd.read_csv(source)
        dates = grab_dates(df)
        rf_rates = grab_LIBOR(dates)
        vols = calc_volatilities(df, length)

        df = pd.concat([df, rf_rates, vols], axis=1)
        handle_strategy(current_directory, query_file, df, length, strike, trading_strategy)
        return


if __name__ == '__main__':
    print('computations main executed')