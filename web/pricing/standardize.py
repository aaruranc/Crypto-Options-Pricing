from pathlib import Path
import pandas as pd
import numpy as np
import time
import datetime
import holidays
import os
from math import ceil


def holiday_length(date_info):
    start_datetime = date_info['start_datetime']
    end_datetime = date_info['end_datetime']
    increment = datetime.timedelta(days=1)

    US_holidays = holidays.US()

    counter_datetime = start_datetime
    k = [counter_datetime]
    count = 1
    while counter_datetime != end_datetime:
        if counter_datetime.weekday() < 5:
            if counter_datetime in US_holidays:
                year = counter_datetime.year
                if holidays.US(years=[year])[counter_datetime] == 'Columbus Day' or \
                        holidays.US(years=[year])[counter_datetime] == 'Veterans Day':
                    count = count + 1
                    k.append(counter_datetime)
            else:
                count = count + 1
                k.append(counter_datetime)
        counter_datetime = counter_datetime + increment
    return count


def weekday_length(date_info):
    start_datetime = date_info['start_datetime']
    end_datetime = date_info['end_datetime']
    increment = datetime.timedelta(days=1)

    counter_datetime = start_datetime
    count = 0
    while counter_datetime != end_datetime:
        if counter_datetime.weekday() < 5:
            count = count + 1
        counter_datetime = counter_datetime + increment
    return count


def move_date(timestamp, shift, date):
    if date == 'M':
        weekday_num = 0
        increment = datetime.timedelta(days=1)
    else:
        weekday_num = 4
        increment = datetime.timedelta(days=-1)
    date = datetime.date.fromtimestamp(timestamp)
    new_date = date
    while new_date.weekday() != weekday_num:
        new_date = new_date + increment
        shift = shift + 1
    data = [int(time.mktime(new_date.timetuple())), shift, date]
    return data


def UNIX_timestamp(val):
    x = int(time.mktime(val.timetuple()))*1000
    return x

def timestamp_convert(start, end):
    start_shift = 0
    end_shift = 0
    start_timestamp = int(time.mktime(datetime.datetime.strptime(start, "%m/%d/%Y").timetuple()))
    end_timestamp = int(time.mktime(datetime.datetime.strptime(end, "%m/%d/%Y").timetuple()))
    diff = (end_timestamp - start_timestamp) // 86400
    start_data = move_date(start_timestamp, start_shift, 'M')
    end_data = move_date(end_timestamp, end_shift, 'F')

    d = {'start': start_data[0], 'start_shift': start_data[1], 'start_datetime': start_data[2],
         'end': end_data[0], 'end_shift': end_data[1], 'end_datetime': end_data[2], 'length': diff + 1}
    return d


def validate(user_parameters):

    print(user_parameters)

    start = user_parameters['start']
    end = user_parameters['end']
    trading_days = user_parameters['trading_days']
    source = Path(user_parameters['source'])

    error = []
    df = pd.read_csv(source)

    day = datetime.timedelta(days=1)
    date_info = timestamp_convert(start, end)

    if trading_days[-1:] == 'H':
        h = holiday_length(date_info)
        correct_length = h
    elif trading_days == 'weekdays':
        w = weekday_length(date_info)
        correct_length = w
    else:
        correct_length = date_info['length']

    n = len(df)
    headers = list(df)

    if n < 10:
        error.append('csv must have at least 10 data points ')
    if 'Date' not in headers:
        error.append('Date not labeled correctly in csv')
    if 'Price' not in headers:
        error.append('Price not labeled correctly in csv')
    if len(headers) > 2:
        error.append('Too Many Columns')
    if df['Date'][0] != start:
        error.append('Start Date Incorrect')
    if df['Date'][n - 1] != end:
        error.append('End Date Incorrect')
    if 'Start Date Incorrect' not in error and 'End Date Incorrect' not in error:
        if n > correct_length + (.02 * n):
            error.append('Duplicate Rows')
        elif n < correct_length - (.02 * n):
            error.append('Missing Rows')

    nonneg = True
    isnum = True

    for index, series in df.iterrows():
        if nonneg:
            if float(df['Price'][index]) <= 0:
                error.append('All Prices must be Greater than 0')
                nonneg = False
        if isnum:
            if np.isnan(float(df['Price'][index])):
                error.append('Prices must be Real Numbers')
                isnum = False

    if not error:

        start_datetime = date_info['start_datetime']
        end_datetime = date_info['end_datetime']
        dummy = start_datetime

        datetime_dates = []
        UNIX_dates = []
        US_holidays = holidays.US()

        if trading_days[-1:] == 'H':
            while dummy != end_datetime:
                if dummy.weekday() < 5:
                    if dummy in US_holidays:
                        year = dummy.year
                        if holidays.US(years=[year])[dummy] == 'Columbus Day' or \
                                holidays.US(years=[year])[dummy] == 'Veterans Day':
                            datetime_dates.append(dummy)
                            UNIX_dates.append(UNIX_timestamp(dummy))
                    else:
                        datetime_dates.append(dummy)
                        UNIX_dates.append(UNIX_timestamp(dummy))
                dummy = dummy + day

        elif trading_days == 'weekdays':
            while dummy != end_datetime:
                if dummy.weekday() < 5:
                    datetime_dates.append(dummy)
                    UNIX_dates.append(UNIX_timestamp(dummy))
                dummy = dummy + day
        else:
            while dummy != end_datetime:
                datetime_dates.append(dummy)
                UNIX_dates.append(UNIX_timestamp(dummy))
                dummy = dummy + day

        datetime_dates.append(end_datetime)
        UNIX_dates.append(UNIX_timestamp(end_datetime))

        d = {'Datetime': datetime_dates, 'Timestamp': UNIX_dates}
        new_df = pd.DataFrame.from_dict(d)
        prices = df['Price'].tolist()

        final_length = len(new_df)
        prices_length = len(prices)
        diff = final_length - prices_length

        if diff > 0:
            spacing = ceil(final_length / diff)

            inserts = 0
            for k in range(spacing, final_length + spacing, spacing):
                if k <= final_length:
                    prices.insert(k, prices[k + inserts])
                else:
                    prices.append(prices[len(prices)-1])
                inserts = inserts + 1

            while len(prices) < final_length:
                prices.append(prices[len(prices) - 1])

            while len(prices) > final_length:
                prices.pop()

        b = {'Price': prices}
        price_df = pd.DataFrame.from_dict(b)
        df = pd.concat([new_df, price_df], axis=1)
        print(df)
        df.to_csv(source, index=False)
        return []
    else:
        os.remove(source)
        return error

def handle_entry(entry):
    if int(entry[-2:]) > 85:
        add_on = '19'
    else:
        add_on = '20'

    val = 0
    if len(entry) == 6:
        val = datetime.date(year=int(add_on + entry[-2:]), month=int(entry[0]), day=int(entry[2]))
    elif len(entry) == 7:
        if entry[1] == '/':
            val = datetime.date(year=int(add_on + entry[-2:]), month=int(entry[0]), day=int(entry[2:4]))
        else:
            val = datetime.date(year=int(add_on + entry[-2:]), month=int(entry[0:2]), day=int(entry[3]))
    elif len(entry) == 8:
        val = datetime.date(year=int(add_on + entry[-2:]), month=int(entry[0:2]), day=int(entry[3:5]))
    return val


def convert_date_to_datetime():

    x = ['LIBOR.csv', 'VIX.csv']
    for file in x:
        df = pd.read_csv(file)
        cols = list(df)
        cols.remove('Date')
        date_df = df['Date']

        k = []
        for index, series in date_df.iteritems():
            a = handle_entry(date_df[index])
            k.append(a)

        d = {'Datetime': k}
        datetime_df = pd.DataFrame.from_dict(d)
        vals = df[cols]
        new_df = pd.concat([datetime_df, vals], axis=1)
        print(new_df)
        new_df.to_csv(file, index=False)

    return


if __name__ == '__main__':

    d = {'start': '7/30/2008', 'end': '7/19/2018', 'trading_days': 'weekdays-H', 'source': 'data/1534366837/AAPL.csv'}

    # convert_date_to_datetime()

    # error = validate(d)
    # print(error)

