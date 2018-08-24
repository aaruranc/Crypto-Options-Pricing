from pathlib import Path
import os
import pandas as pd
from math import sqrt, log, exp, ceil
from scipy.stats import norm
# import pricing.strategies as strategies
import strategies
import numpy as np
import copy


def handle_strategy(query, query_file):

    strategy = query['trading_strategy']
    new_strikes = strategies.missing_strikes(query, strategy)

    if new_strikes:
        print(new_strikes)
        new_query = copy.deepcopy(query)
        for val in new_strikes:
            new_query.update({'strike': str(val)})
            new_query.update({'trading_strategy': 'Straddles'})
            search_and_compute(new_query)

    strategies.compute(query, query_file, strategy)

    df = pd.read_csv(query_file)
    print(df)
    return


def option_payoff(df, parameters, type, price):

    index = int(parameters['index'])
    time = int(parameters['days'])
    new_index = index + time

    strike = parameters['strike']
    expiration_price = df['Price'][new_index]

    if type == 'Calls':
        if expiration_price < strike:
            return -price
        else:
            return expiration_price - strike - price
    elif type == 'Puts':
        if expiration_price > strike:
            return -price
        else:
            return strike - expiration_price - price
    else:
        return 0


def put_price(parameters):
    d1 = parameters['d1']
    d2 = parameters['d2']
    spot = parameters['spot']
    strike = parameters['strike']
    rf = parameters['rf']
    length = parameters['length']

    return (norm.cdf(-d2) * strike * exp(-rf * length)) - (norm.cdf(-d1) * spot)


def call_price(parameters):
    d1 = parameters['d1']
    d2 = parameters['d2']
    spot = parameters['spot']
    strike = parameters['strike']
    rf = parameters['rf']
    length = parameters['length']

    return (norm.cdf(d1) * spot) - (norm.cdf(d2) * strike * exp(-rf * length))


def calc_d2(d1, vol, length):
    return d1 - (vol * sqrt(length))


def calc_d1(vol, length, ratio, rf):
    return (log(ratio) + (length * (rf + ((vol ** 2) / 2)))) / (vol * sqrt(length))


def black_scholes_dict(query, df, index):

    strike_ratio = query['strike']
    ratio = 100 / float(strike_ratio)
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

    d = {'d1': d1, 'd2': d2, 'strike': strike, 'spot': spot, 'rf': rf, 'length': year_length, 'days': length,
         'index': index}
    return d


def new_strike_data(query, query_file, df):

    length = int(query['option_length'])
    strike = query['strike']
    c = strike + '-Calls'
    cp = c + '-P'
    cr = c + '-ROI'

    p = strike + '-Puts'
    pp = p + '-P'
    pr = p + '-ROI'

    j = []
    k = []
    l = []

    s = []
    t = []
    u = []

    big_container = [j, k, l, s, t, u]
    small_container = [k, l, t, u]

    df_length = len(df)

    for index, series in df.iterrows():
        if index < length + 1:
            for name in big_container:
                name.append('')
        else:
            parameters = black_scholes_dict(query, df, index)
            j.append(call_price(parameters))
            s.append(put_price(parameters))

            if (index + length) < df_length:
                k.append(option_payoff(df, parameters, 'Calls', j[-1]))
                l.append((k[-1] / j[-1]) * 100)
                t.append(option_payoff(df, parameters, 'Puts', s[-1]))
                u.append((t[-1] / s[-1]) * 100)
            else:
                for name in small_container:
                    name.append('')

    d = {c: j, cp: k, cr: l, p: s, pp: t, pr: u}
    new_df = pd.DataFrame.from_dict(d)
    df = pd.concat([df, new_df], axis=1)
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
    if df_length == date_length:
        return df
    else:
        shorter = False
        diff = date_length - df_length
        stepsize = ceil(df_length / diff)
        if diff > 0:
            shorter = True

    if title == '':
        name = 'VIX-Close'
        df_header = 'VIX'
    else:
        name = title + '-LIBOR'
        df_header = name

    if shorter:
        vals = df[name].tolist()
        counter = 0
        while (len(vals) < date_length):
            x = int(((counter + 1) * stepsize) + counter)
            if x > len(vals):
                vals.append(vals[len(vals) - 1])
            else:
                vals.insert(x, vals[x-1])
            counter = counter + 1
        d = {df_header: vals}
        df = pd. DataFrame.from_dict(d)

    else:
        vals = df[name].tolist()
        counter = 0
        while (len(vals) > date_length):
            x = -1 * int(((counter + 1) * stepsize) - counter)
            if x >= len(vals):
                vals.pop()
            else:
                vals.pop(x)
            counter = counter + 1
        d = {df_header: vals}
        df = pd.DataFrame.from_dict(d)

    return df


def grab_data(dates, length=0):
    if length == 0:
        df = pd.read_csv('VIX.csv', usecols=['Datetime', 'VIX-Close'])
    else:
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
        num = int(length) // 30
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

        # Compute Length of Source DataFrame
        date_length = len(df['Datetime'])

        # Copy VIX data between Start & End dates
        VIX = grab_data(dates)
        updated_VIX = fix_length(VIX, date_length)

        # Copy LIBOR data between Start & End dates
        LIBOR = grab_data(dates, length=length)
        updated_LIBOR = fix_length(LIBOR, date_length, title=option_length)

        # Calculate option_length Volatility for all dates
        trading_days = query['trading_days']
        vols = calc_volatility(df, length, trading_days)

        # Concatenate DataFrames
        df = pd.concat([df, updated_VIX, updated_LIBOR, vols], axis=1)

        # Calculate and Append Puts and Calls for user-specified combination of Length and Strike
        new_strike_data(query, query_file, df)

        # Compute Results from user-specified Option Strategy
        handle_strategy(query, query_file)
        return


if __name__ == '__main__':
    print('computations main executed')

    test_query = {'trading_strategy': 'Strangles', 'option_length': '30', 'strike': '54',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv',
                  'trading_days': 'weekdays-H'}

    search_and_compute(test_query)




    # search_and_compute(test_query)