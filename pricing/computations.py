from pathlib import Path
import os
import pandas as pd
from math import sqrt, log, ceil
import pricing.strategies as strategies
from pricing.black_scholes import new_strike_data
import numpy as np
import copy
import datetime
import boto3
from io import StringIO


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
        if length == 1:
            length = 2

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

    if title == '':
        name = 'VIX-Close'
        df_header = 'VIX'
    else:
        name = title + '-LIBOR'
        df_header = name

    df_length = len(df)
    if df_length == date_length:
        new_df = df[df_header]
        return new_df
    else:
        shorter = False
        diff = date_length - df_length
        stepsize = df_length / diff
        if diff > 0:
            shorter = True

    vals = df[name].tolist()
    if shorter:
        counter = 0
        while len(vals) < date_length:
            x = ceil(((counter + 1) * stepsize) + counter)
            if x >= len(vals):
                vals.append(vals[len(vals) - 1])
            else:
                vals.insert(x, vals[x-1])
            counter = counter + 1
    else:
        counter = 0
        while len(vals) > date_length:
            x = ceil(((counter + 1) * stepsize) + counter)
            if x >= len(vals):
                vals.pop()
            else:
                vals.pop(x)

            counter = counter + 1

    d = {df_header: vals}
    new_df = pd.DataFrame.from_dict(d)

    return new_df


def update_datetime(df, input, endpoint):

    info = str(input).rsplit('-')
    yr = int(info[0])
    mo = int(info[1])
    date = ''

    if endpoint == 'Start':
        if mo == 1:
            date = str(yr - 1) + '-12'
        else:
            if mo < 11:
                date = str(yr) + '-0' + str(mo-1)
            else:
                date = str(yr) + '-' + str(mo-1)

    elif endpoint == 'End':
        if mo == 12:
            date = str(yr + 1) + '-01'
        else:
            if mo < 9:
                date = str(yr) + '-0' + str(mo+1)
            else:
                date = str(yr) + '-' + str(mo+1)

    list_index = -1
    n = len(df)
    for index in range(n):
        if df['Datetime'][index][:7] == date:
            list_index = index
            break

    if list_index == -1:
        if endpoint == 'Start':
            list_index = 0
        elif endpoint == 'End':
            list_index = n

    start = ''
    end = ''
    day = ''
    if endpoint == 'Start':
        day = datetime.timedelta(days=1)
        start = list_index
        if start + 62 >= n:
            end = n
        else:
            end = start + 62
    elif endpoint == 'End':
        day = datetime.timedelta(days=-1)
        end = list_index
        if end - 62 < 0:
            start = 0
        else:
            start = end - 62

    temp = input
    trimmed_dates = (df['Datetime'].loc[start:end]).tolist()

    while str(temp) not in trimmed_dates:
        temp = temp + day

    return temp


def grab_index(df, endpoint, started=False):

    endpoint_str = str(endpoint)

    for index in range(len(df)):
        if not started:
            if df['Datetime'][index] == endpoint_str:
                return index
            continue
        elif started:
            if df['Datetime'][index] == endpoint_str:
                return index
            continue
    return -1


def string_to_datetime(string):
    return datetime.date(year=int(string[:4]), month=int(string[5:7]), day=int(string[8:10]))


def grab_data(dates, length=0):

    # Find start/end indices of VIX and LIBOR csv's and return as DataFrames
    if length == 0:
        df = pd.read_csv('VIX.csv', usecols=['Datetime', 'VIX-Close'])
    else:
        header = option_label(length) + '-LIBOR'
        df = pd.read_csv('LIBOR.csv', usecols=['Datetime', header])

    start = dates['start']
    end = dates['end']
    start_index = grab_index(df, start)
    end_index = grab_index(df, end, started=True)

    needs_updated = []
    if start_index == -1:
        needs_updated.append('Start')
    if end_index == -1:
        needs_updated.append('End')

    if needs_updated:
        start_datetime = string_to_datetime(start)
        end_datetime = string_to_datetime(end)

        for endpoint in needs_updated:
            if endpoint == 'Start':
                start_datetime = update_datetime(df, start_datetime, 'Start')
            else:
                end_datetime = update_datetime(df, end_datetime, 'End')

        start_index = grab_index(df, start_datetime)
        end_index = grab_index(df, end_datetime, started=True)

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

    test_query = {'trading_strategy': 'Calls', 'option_length': '5', 'strike': '100', 'request': 'pdf',
                  'source': '1535661792-SQ',
                  'S3_info': {'bucket': 'optionbacktester', 'key': 'AKIAJZ2U45FY6TBTUW3Q',
                              'secret': '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'},
                  'trading_days': 'weekdays-H'}

    # Initialize Query data to probe/generate information from User Directory
    length = int(query['option_length'])
    # current_directory = Path(query['current_directory'])
    option_length = option_label(length)
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(query['S3_info']['bucket'])

    source = query['source']
    source_file = source + '.csv'
    query_file = source + '-' + str(length) + '.csv'


    obj = s3.Object(bucket, source_file)
    obj2 = s3.Object(bucket, query_file)
    objs = list(bucket.objects.filter(Prefix=query_file))


    data = bucket.Object(source_file).get()['Body'].read().decode('utf-8')
    testdata = StringIO(data)
    df = pd.read_csv(testdata)

    # loc = option_length + '.csv'
    # query_file = current_directory / loc


    # Check if the required File exists
    if len(objs) > 0 and objs[0].key == query_file:

        # Initialize Dataframe to compare Query against previous computations
        # df = pd.read_csv(query_file)

        data = bucket.Object(query_file).get()['Body'].read().decode('utf-8')
        parsed_data = StringIO(data)
        df = pd.read_csv(parsed_data)

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
        data = bucket.Object(source_file).get()['Body'].read().decode('utf-8')
        parsed_data = StringIO(data)
        df = pd.read_csv(parsed_data)

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

    test_query = {'trading_strategy': 'Calls', 'option_length': '5', 'strike': '100', 'request': 'pdf',
                  'name': '1535661792-SQ',
                  'S3_info': {'bucket': 'optionbacktester', 'key': 'AKIAJZ2U45FY6TBTUW3Q',
                              'secret': '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'},
                  'trading_days': 'weekdays-H'}


    search_and_compute(test_query)
