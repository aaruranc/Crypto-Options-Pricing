from pathlib import Path
import os
import pandas as pd
from math import sqrt, log, exp, ceil
from scipy.stats import norm
import strategies
import numpy as np

def additional_strikes(query, new_strikes):
    new_query = query
    for val in new_strikes:
        new_query.update({'strike': val})
        search_and_compute(new_query)
    return

def handle_strategy(query, query_file):

    strategy = query['trading_strategy']
    if strategy == 'Calls' or strategy == 'Puts':
        return

    new_strikes = strategies.missing_strikes(query, query_file, strategy)
    if new_strikes:
        additional_strikes(query, new_strikes)

    if strategy == 'Straddles':
        strategies.straddle(query, query_file)
    elif strategy == 'Bear-Spreads':
        strategies.bear_spreads(query, query_file)
    # elif strategy == 'Bull-Spreads':
    #     strategies.bull_spreads(query, query_file)
    # elif strategy == 'Box-Spreads':
    #     strategies.box_spreads(query, query_file)
    # elif strategy == 'Butterfly-Spreads':
    #     strategies.butterfly_spreads(query, query_file)
    # elif strategy == 'Calendar-Spreads':
    #     strategies.calendar_spreads(query, query_file)
    # elif strategy == 'Straps':
    #     strategies.straps(query, query_file)
    # elif strategy == 'Strips':
    #     strategies.strips(query, query_file)
    # elif strategy == 'Strangles':
    #     strategies.strangles(query, query_file)
    return


########## REWRITE B-S Code here


def put_price(parameters):
    d1 = parameters['d1']
    d2 = parameters['d2']
    spot = parameters['spot']
    strike = parameters['strike']
    rf = parameters['rf']
    length = parameters['length']

    z = (norm.cdf(-d2) * strike * exp(-rf * length)) - (norm.cdf(-d1) * spot)
    return z


def call_price(parameters):
    d1 = parameters['d1']
    d2 = parameters['d2']
    spot = parameters['spot']
    strike = parameters['strike']
    rf = parameters['rf']
    length = parameters['length']

    y = (norm.cdf(d1) * spot) - (norm.cdf(d2) * strike * exp(-rf * length))
    return y


def calc_d2(d1, vol, length):
    x = d1 - (vol * sqrt(length))
    return x


def calc_d1(vol, length, ratio, rf):
    w = (log(ratio) + (length * (rf + ((vol ** 2) / 2)))) / (vol * sqrt(length))
    return w


def black_scholes_dict(query, df, index):

    test_query = {'trading_strategy': 'Calls', 'option_length': '10', 'strike': '100',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv',
                  'trading_days': 'weekdays-H'}

    ratio = 100 / float(query['strike'])
    spot = float(df['Price'][index])
    strike = spot / ratio
    length = query['option_length']
    year_length = float(length) / 365

    title = option_label(length)
    rf_header = title + '-LIBOR'
    vol_header = title + '-VM'
    rf = float(df[rf_header][index]) / 100
    vol = float(df[vol_header][index]) / 100

    d1 = calc_d1(vol, year_length, ratio, rf)
    d2 = calc_d2(d1, vol, year_length)

    d = {'d1': d1, 'd2': d2, 'strike': strike, 'spot': spot, 'rf': rf, 'length': year_length}
    return d


def new_strike_data(query, query_file, df):

    length = int(query['option_length'])
    strike = query['strike']
    c = strike + '-Calls'
    p = strike + '-Puts'

    j = []
    k = []

    for index, series in df.iterrows():
        if index < length + 1:
            j.append('')
            k.append('')
        else:
            parameters = black_scholes_dict(query, df, index)
            j.append(call_price(parameters))
            k.append(put_price(parameters))

    d = {c: j, p: k}
    new_df = pd.DataFrame.from_dict(d)
    df = pd.concat([df, new_df], axis=1)
    print(df)
    df.to_csv(query_file, index=False)
    return


def vol_mean(df, length, index, trading_days):
    if index < length + 1:
        return ''
    else:
        if trading_days == 'weekdays':
            multiplier = 16
        elif trading_days == 'weekends':
            multiplier = sqrt(365)
        else:
            multiplier = sqrt(252)

        k = []
        for n in range((index - length), index):
            k.append(log(df['Price'][n+1] / df['Price'][n]))
        x = np.std(k, ddof=1)
        return multiplier * 100 * x


def calc_volatility(df, length, trading_days):

    title = option_label(length) + '-VM'
    k = []
    for index, series in df.iterrows():
        x = vol_mean(df, length, index, trading_days)
        k.append(x)
    d = {title: k}
    df = pd.DataFrame.from_dict(d)
    return df


def fix_length(df, date_length, title=''):
    df_length = len(df)
    # print(df)
    # print(df_length)
    # print(date_length)
    if df_length == date_length:
        return df
    else:
        shorter = False
        diff = date_length - df_length
        stepsize = ceil(df_length / diff)
        if diff > 0:
            shorter = True

    if shorter:
        if title == '':
            name = 'VIX-Close'
        else:
            name = title + '-LIBOR'
        vals = df[name].tolist()
        counter = 0
        while (len(vals) < date_length):
            x = int(((counter + 1) * stepsize) + counter)
            # print(stepsize)
            # print(x)
            # print(date_length)
            if x > len(vals):
                vals.append(vals[len(vals) - 1])
            else:
                vals.insert(x, vals[x-1])
            counter = counter + 1
        d = {name: vals}
        df = pd. DataFrame.from_dict(d)

    else:
        if title == '':
            name = 'VIX-Close'
        else:
            name = title + '-LIBOR'
            vals = df[name].tolist()
        counter = 0
        while (len(vals) > date_length):
            x = -1 * int(((counter + 1) * stepsize) - counter)
            if x >= len(vals):
                vals.pop()
            else:
                vals.pop(x)
            counter = counter + 1
        d = {name: vals}
        df = pd.DataFrame.from_dict(d)

    return df


def grab_data(dates, length=0):
    if length == 0:
        print('VIX started')
        df = pd.read_csv('VIX.csv', usecols=['Datetime', 'VIX-Close'])
    else:
        print('LIBOR started')
        header = option_label(length) + '-LIBOR'
        df = pd.read_csv('LIBOR.csv', usecols=['Datetime', header])

    started = False
    start_index = 0
    end_index = 0
    start = dates['start']
    end = dates['end']

    for index, series in df.iterrows():
        if not started:
            if df['Datetime'][index] == start:
                started = True
                start_index = index
            continue
        elif started:
            if df['Datetime'][index] == end:
                end_index = index
                break
            continue

    data = (df.loc[start_index:end_index]).copy()
    data.reset_index(drop=True, inplace=True)
    return data


def find_dates(df):

    n = len(df)
    e = n - 1
    start_date = df['Datetime'][0]
    end_date = df['Datetime'][e]
    d = {'start': start_date, 'end': end_date}
    return d


def option_label(length):

    if int(length) < 15:
        option_length = str(length) + '-Day'
    elif 14 < int(length) < 365:
        num = length // 30
        option_length = str(num) + '-Month'
    else:
        option_length = '1-Year'
    return option_length


def search_and_compute(query):

    # Initialize Query data to probe/generate information from User Directory
    length = int(query['option_length'])
    current_directory = Path(query['current_directory'])
    option_length = option_label(length)
    loc = option_length + '.csv'
    query_file = current_directory / loc

    # Check if the required File exists
    if os.path.isfile(query_file):

        # Initialize Dataframe to compare Query against previous computations
        df = pd.read_csv(query_file)
        headers = list(df)
        strike = query['strike']
        strategy = query['trading_strategy']
        test = strike + '-Calls'

        # Check if Query for user-specified Strike has already been made
        if test in headers:
            method = strike + '-' + strategy
            # Check if Strategy has already been computed for user-specified Strike
            if method in headers:
                return
            else:
                handle_strategy(query, query_file)
                return
        else:
            new_strike_data(query, query_file, df)
            handle_strategy(query, query_file)
            return

    else:

        # Create DataFrame from user-info
        source = Path(query['source'])
        df = pd.read_csv(source)
        # Create Dictionary of Start & End dates
        dates = find_dates(df)
        print(dates)
        # Compute Length of Source DataFrame
        date_length = len(df['Datetime'])
        # Copy VIX data between Start & End dates
        VIX = grab_data(dates)
        updated_VIX = fix_length(VIX, date_length)
        # Copy LIBOR data between Start & End dates
        LIBOR = grab_data(dates, length=length)
        print(LIBOR)
        updated_LIBOR = fix_length(LIBOR, date_length, title=option_length)
        # Calculate option_length Volatility for all dates
        trading_days = query['trading_days']
        vols = calc_volatility(df, length, trading_days)
        # Concatenate DataFrames
        df = pd.concat([df, updated_VIX, updated_LIBOR, vols], axis=1)
        print(df)
        # Calculate and Append Puts and Calls for user-specified combination of Length and Strike
        new_strike_data(query, query_file, df)

        # # STILL HAVE TO COMPUTE PAYOFFS AND RETURNS FROM NEW STRIKES
        # payoffs_and_returns(query, query_file, df, new_strike=True)


        # Compute Results from user-specified Option Strategy
        # handle_strategy(query, query_file)
        return


if __name__ == '__main__':
    print('computations main executed')

    test_query = {'trading_strategy': 'Calls', 'option_length': '10', 'strike': '100',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv',
                  'trading_days': 'weekdays-H'}

    search_and_compute(test_query)

    # loc = Path(test_query['current_directory']) / '9-Day.csv'
    # df = pd.read_csv(loc)
    # new_strike_data(test_query, loc, df)



    # annual_rf = (1.121521739) ** (365 / 9)
    #
    # x = {'i': 1390, 'l': 0.024657534246575342, 'st': 78.66573000000001, 'sp': 71.5143,
    #      'r': 0.9090909090909091, 'rf': 1.121521739, 'v': 48.10019478494585, 'd1': 3.764296825178816,
    #      'd2': -3.7887409643280927, 'c': 71.50239022171021, 'p': 78.41845694879935}
    #
    # # d1 = 3.764296825178816
    # # d2 = -3.7887409643280927
    # # n_d1 = 0.9999164907998107
    # # n_d2 = 7.570634363292039e-05
    #
    # calc_call = 71.50239022171021
    # calc_put = 8.41845694879935
    #
    # web_call = .28 / .29
    # web_put = 7.3 / 7.4
    #
    # # j = norm.ppf(.1118)
    # # k = -norm.ppf(.8882)
    # # l = norm.ppf((.0214 / (x['spot'] * sqrt(x['length']))) * exp(x['rf'] * x['length']))
    # # temp = (.0352 * x['spot'] * sqrt(x['length']) * x['vol'])
    # # print(temp)
    # # m = norm.ppf(temp)
    # # y = (j + k + l + m) / 4
    # # print('d1')
    # # print(j, k, l, m)
    # # print(y)
    # #
    # # a = norm.ppf((.0019 / (x['strike'] * x['length'])) * exp(x['rf'] * x['length']))
    # # b = -norm.ppf((.00175 / (x['strike'] * x['length'])) * exp(x['rf'] * x['length']))
    # # c = norm.ppf((.0214 / (x['strike'] * sqrt(x['length']))) * exp(x['rf'] * x['length']))
    # # d = norm.ppf(exp(x['rf'] * x['length']) * ((.0214 / (x['strike'] * sqrt(x['length']))) * exp(x['rf'] * x['length'])) / x['strike'])
    # # z = (a + b + c + d) / 4
    # # print('d2')
    # # print(a, b, c, d)
    # # print(z)
    #
    # # d1 = -1.217011
    # # d2 = -3.095
    #
    # delta = .1107
    # rho = .0019
    # d1 = norm.ppf(delta)
    # d2 = norm.ppf((rho / (x['st'] * x['l'])) * exp(x['rf'] * x['l']))
    #
    #
    # c = x['sp'] * norm.cdf(d1) - (x['st'] * exp(-1 * x['rf'] * x['l']) * norm.cdf(d2))
    # p = (x['st'] * exp(-1 * x['rf'] * x['l']) * norm.cdf(-d2)) - x['sp'] * norm.cdf(-d1)
    #
    # print(c)
    # print(p)


    # search_and_compute(test_query)