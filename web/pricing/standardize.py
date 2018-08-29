from pathlib import Path
import pandas as pd
import numpy as np
import time
import datetime
import holidays
import os
from math import ceil


def finish_validation(source, dates, prices):

    k = dates
    k.update({'Price': prices})
    df = pd.DataFrame.from_dict(k)
    df.to_csv(source, index=False)
    return


def match_datetimes(df, d):

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
                prices.append(prices[len(prices) - 1])
            inserts = inserts + 1

        while len(prices) < final_length:
            prices.append(prices[len(prices) - 1])

        while len(prices) > final_length:
            prices.pop()

    return prices


def UNIX_timestamp(val):
    x = int(time.mktime(val.timetuple()))*1000
    return x


def generate_timestamps(date_info, trading_days):

    start_datetime = date_info['start_datetime']
    end_datetime = date_info['end_datetime']
    dummy = start_datetime
    day = datetime.timedelta(days=1)

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
    return d


def error_check(df, date_info, start, end, correct_length):

    error = []
    n = len(df)
    headers = list(df)

    webapp_start = datetime.date(year=2001, month=1, day=1)
    webapp_end = datetime.date(year=2018, month=8, day=1)

    if date_info['start_datetime'] < webapp_start or date_info['end_datetime'] > webapp_end:
        error.append('Dates are out of range. Please trim csv to time series data between 1/1/01 and 8/1/18')
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
            error.append('Duplicate Rows. Is Trading Days selection correct?')
        elif n < correct_length - (.02 * n):
            error.append('Missing Rows. Is Trading Days selection correct?')

    nonneg = True
    isnum = True

    if 'Price' in headers:
        for index, series in df.iterrows():
            if nonneg:
                if float(df['Price'][index]) <= 0:
                    error.append('All Prices must be Greater than 0')
                    nonneg = False
            if isnum:
                if np.isnan(float(df['Price'][index])):
                    error.append('Prices must be Real Numbers')
                    isnum = False

    return error


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


def validate(user_parameters):

    # Initialize input data
    start = user_parameters['start']
    end = user_parameters['end']
    trading_days = user_parameters['trading_days']
    source = Path(user_parameters['source'])

    # Convert input into datetime and perform preliminary calculations
    date_info = timestamp_convert(start, end)

    # Compute days between start and end
    if trading_days[-1:] == 'H':
        correct_length = holiday_length(date_info)
    elif trading_days == 'weekdays':
        correct_length = weekday_length(date_info)
    else:
        correct_length = date_info['length']

    # Check compatibility of user input to uploaded file and O-B requirements
    df = pd.read_csv(source)
    error = error_check(df, date_info, start, end, correct_length)

    if not error:

        # Adjust times to match correct_length
        dates = generate_timestamps(date_info, trading_days)

        # Adjust prices to match correct_length
        prices = match_datetimes(df, dates)

        # Generate Dataframe from validated information
        finish_validation(source, dates, prices)
        return []
    else:
        os.remove(source)
        return error


if __name__ == '__main__':

    d = {'start': '7/30/2008', 'end': '7/19/2018', 'trading_days': 'weekdays-H', 'source': 'data/1534366837/AAPL.csv'}

    # error = validate(d)
    # print(error)

