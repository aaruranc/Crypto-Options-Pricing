from pathlib import Path
import os
import pandas as pd
from math import sqrt, log, ceil
import pricing.strategies as strategies
from pricing.black_scholes import new_strike_data
# import strategies
# from black_scholes import new_strike_data
import numpy as np
import copy


def handle_strategy(query, query_file):

    strategy = query['trading_strategy']
    new_strikes = strategies.missing_strikes(query, strategy)

    if new_strikes:
        base = ['Calls', 'Puts']
        for val in new_strikes:
            for header in base:
                new_query = copy.deepcopy(query)
                new_query.update({'strike': str(val), 'trading_strategy': header})
                title = str(val) + '-' + header
                df = pd.read_csv(query_file)

                if title not in list(df):
                    new_strike_data(new_query, query_file, df)

    strategies.compute(query, query_file, strategy)

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
            # print(x)
            # print(len(vals))
            if x == 0:
                vals.insert(x, vals[x])
            elif x > len(vals):
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

    # Find start/end indices of VIX and LIBOR csv's and return as DataFrames
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

    # end_datetime = datetime.date(year=int(end[:4]), month=int(end[5:7]), day=int(end[8:10]))
    # if end not in df['Datetime']:
    #     day = datetime.timedelta(days=1)
    #     end = end_datetime + day
    #     if end not in df['Datetime']:
    #         end = end + day
    #         if end not in df['Datetime']:
    #             end = end + day
    #
    # print(end)

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

    # Find Start and End Date and return as dictionary
    n = len(df)
    e = n - 1
    start_date = df['Datetime'][0]
    end_date = df['Datetime'][e]

    return {'start': start_date, 'end': end_date}


def option_label(length):

    # Returns DataFrame column title for user-specified Option length
    if int(length) < 15:
        return str(length) + '-Day'
    elif 14 < int(length) < 365:
        num = int(length) // 30
        return str(num) + '-Month'
    else:
        return '1-Year'


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

    test_query = {'trading_strategy': 'Bull-Spreads', 'option_length': '90', 'strike': '100',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv',
                  'trading_days': 'weekdays-H'}

    search_and_compute(test_query)
