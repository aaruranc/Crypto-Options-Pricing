import pandas as pd
from pathlib import Path
from collections import OrderedDict


def validate_date(user_df, check, val):

    # Still has to check whether the dates are in bounds of the csv

    yr = int(check[-2:])
    mo = int(check[:2])
    da = int(check[3:5])
    if yr < 19:
        yr = yr + 2000
    else:
        yr = yr + 1900
    pt = date(yr, mo, da)

    if val == 0:
        pt = find_date(pt, 0)
    elif val == 1:
        pt = find_date(pt, 4)
    return pt


def find_date(date, weekday_num):

    dt = timedelta(1)
    user = date

    if weekday_num == 0:
        while user.weekday() != weekday_num:
            user = user + dt
    if weekday_num == 4:
        while user.weekday() != 4:
            user = user - dt
    year = str(user.year)[-2:]
    month = str(user.month)
    day = str(user.day)
    date = month + '/' + day + '/' + year
    df_date = adjust_string(date, len(date))

    return df_date


def fit_dates(user_df, start, end):

    start_index = find_index(user_df, start)
    end_index = find_index(user_df, end)
    l = []
    for i in range(start_index, (end_index + 1)):
        l.append(i)
    user_df = user_df.loc[l]
    user_df.reset_index(drop=True, inplace=True)
    return user_df


def find_index(user_df, date):
    for index, series in user_df.iterrows():
        if adjust_string(user_df['Date'][index], len(user_df['Date'][index])) == date:
            return index


def adjust_string(date, length):
    if length == 6:
        new_date = "0" + date[0:2] + "0" + date[2:]
        return  new_date
    elif length == 7:
        if date[1] == "/":
            new_date = "0" + date
            return new_date
        else:
            new_date = date[0:3] + "0" + date[3:]
            return new_date
    elif length == 8:
        return date

def generate_dates(libor_df, start, end):

    libor_start = 0
    libor_end = 0
    for series, index in libor_df.iterrows():
        if adjust_string(libor_df['Date'][series], len(libor_df['Date'][series])) == start:
            libor_start = series
        elif adjust_string(libor_df['Date'][series], len(libor_df['Date'][series])) == end:
            libor_end = series

    libor_subset = []
    for i in range(libor_start, libor_end + 1):
        libor_subset.append(i)

    return libor_subset


def select_LIBOR(option_lengths):

    libor_rates = ['Date']
    for length in option_lengths:
        if length == 1:
            libor_rates.append('1-Day')
        elif 1 < length <= 7:
            if '1-Day' not in libor_rates:
                libor_rates.append('1-Day')
            if '7-Day' not in libor_rates:
                libor_rates.append('7-Day')
        elif 7 < length <= 30:
            if '7-Day' not in libor_rates:
                libor_rates.append('7-Day')
            if '1-Month' not in libor_rates:
                libor_rates.append('1-Month')
        elif 30 < length <= 60:
            if '1-Month' not in libor_rates:
                libor_rates.append('1-Month')
            if '2-Month' not in libor_rates:
                libor_rates.append('2-Month')
        elif 60 < length <= 90:
            if '2-Month' not in libor_rates:
                libor_rates.append('2-Month')
            if '3-Month' not in libor_rates:
                libor_rates.append('3-Month')
        elif 90 < length <= 180:
            if '3-Month' not in libor_rates:
                libor_rates.append('3-Month')
            if '6-Month' not in libor_rates:
                libor_rates.append('6-Month')
        elif 180 < length:
            if '6-Month' not in libor_rates:
                libor_rates.append('6-Month')
            if '1-Year' not in libor_rates:
                libor_rates.append('1-Year')
    return libor_rates


def extend_LIBOR(trimmed_libor_rates, libor_lengths, user_length):

    headers = OrderedDict.fromkeys(libor_lengths, [])
    df = pd.DataFrame.from_dict(headers)
    d = {}

    weekday = 0
    total = 0
    for index, series in trimmed_libor_rates.iterrows():
        if total == user_length-1:
            for title in headers:
                d.update({title: trimmed_libor_rates[title][index]})
            df = df.append(d, ignore_index=True)
            break

        if weekday == 4:
            weekday = 0
            total = total + 3
            for title in headers:
                d.update({title: trimmed_libor_rates[title][index]})
            df = df.append(d, ignore_index=True)
            d.update({'Date': 'XXXXX'})
            df = df.append(d, ignore_index=True)
            df = df.append(d, ignore_index=True)

        else:
            weekday = weekday + 1
            total = total + 1
            for title in headers:
                d.update({title: trimmed_libor_rates[title][index]})
            df = df.append(d, ignore_index=True)
    return df


def synthetic_LIBOR(option_lengths, weeklong_rf_df):

    user_demand = []
    supply = []
    public_data = [1, 7, 30, 60, 90, 180, 365]
    for length in option_lengths:
        if length not in public_data:
            user_demand.append(length)
        elif length in public_data:
            supply.append(length)

    # Freshest line of code ever written
    if not user_demand:
        return

    demand_headers = []
    for num in user_demand:
        if num <= 14:
            title = str(num) + '-Day'
            demand_headers.append(title)
        else:
            month = num / 30
            title = str(month)[0] + '-Month'
            demand_headers.append(title)

    supply_headers = []
    for num in supply:
        if num <= 14:
            title = str(num) + '-Day'
            supply_headers.append(title)
        elif num == 365:
            supply_headers. append('1-Year')
        else:
            month = num / 30
            title = str(month)[0] + '-Month'
            supply_headers.append(title)

    d = OrderedDict.fromkeys(demand_headers, [])
    df = pd.DataFrame.from_dict(d)

    for series, index in weeklong_rf_df.iterrows():
        count= 0
        for title in demand_headers:
            num = user_demand[count]
            d.update({title: bootstrap_LIBOR(weeklong_rf_df, num, series)})
            count = count + 1
        df = df.append(d, ignore_index=True)

    risk_free_rates = pd.concat([weeklong_rf_df, df], axis=1)
    rf_df = risk_free_rates.drop('Date', 1)
    return rf_df


def bootstrap_LIBOR(weeklong_rf_df, num, series):

    if num < 7:
        left_bound = '1-Day'
        right_bound = '7-Day'
        l = 1
        r = 7
    elif 7 < num < 30:
        left_bound = '7-Day'
        right_bound = '1-Month'
        l = 7
        r = 30
    elif 30 < num < 60:
        left_bound = '1-Month'
        right_bound = '2-Month'
        l = 30
        r = 60
    elif 60 < num < 90:
        left_bound = '2-Month'
        right_bound = '3-Month'
        l = 60
        r = 90
    elif 90 < num < 180:
        left_bound = '3-Month'
        right_bound = '6-Month'
        l = 90
        r = 180
    else:
        left_bound = '6-Month'
        right_bound = '1-Year'
        l = 180
        r = 365

    y = weeklong_rf_df[right_bound][series] - weeklong_rf_df[left_bound][series]
    x = r - l
    m = y / x

    if m == 0:
        return weeklong_rf_df[right_bound][series]
    else:
        new = ((m * (num - l)) + weeklong_rf_df[left_bound][series])
        return new


def header_label(length):

    time = ''
    add_on = ''
    if length <= 14:
        time = str(length)
        add_on = '-Day'
    elif 30 <= length < 300:
        time = str(length // 30)[:1]
        add_on = '-Month'
    elif 300 <= length < 365:
        time = str(length // 30)[:2]
        add_on = '-Month'
    elif length == 365:
        time = str(length // 365)[:1]
        add_on = '-Year'

    name = time + add_on
    return name


def volatility_measures(option_lengths, user_df):

    vol_headers = []
    for length in option_lengths:
        name = header_label(length)
        mean = name + '-Vol-Mean'
        no_mean = name + '-Vol-No-Mean'

        vol_headers.append(mean)
        vol_headers.append(no_mean)

    d = OrderedDict.fromkeys(vol_headers, [])
    df = pd.DataFrame.from_dict(d)

    for index, series in user_df.iterrows():
        df = df.append(volatility_calcs(user_df, option_lengths, vol_headers, index), ignore_index=True)

    return df


def volatility_calcs(user_df, option_lengths, vol_headers, index):
    if index == 0:
        return {}

    a = []
    d = {}

    for step in option_lengths:
        if step < index + 1:
            a.append(volatility_mean(user_df, index, step))
            a.append(volatility_no_mean(user_df, index, step))

    count = 0
    for val in a:
        d.update({vol_headers[count]: val})
        count = count + 1
    return d


def volatility_mean(user_df, index, step):
    if step == 1:
        return 0

    s = 0
    for i in range((index - step), index):

        if i >= 1:
            log_return = log(user_df['Price'][i] / user_df['Price'][i-1])
        else:
            log_return = 0
        s = s + log_return

    mu = s / step
    total = 0

    for j in range((index - step), index):

        if j >= 1:
            diff = (log(user_df['Price'][j] / user_df['Price'][j-1]) - mu) ** 2
        else:
            diff = 0
        total = total + diff

    vol = (sqrt(total / (step - 1))) * sqrt(365)
    return vol


def volatility_no_mean(user_df, index, step):
    if step == 1:
        if index >= 1:
            log_return = log(user_df['Price'][index] / user_df['Price'][index - 1])
            annualized = sqrt(365) * (log_return ** 2)
            return annualized

    total = 0
    for j in range((index - step), index):
        if j >= step + 1:
            diff = (log(user_df['Price'][j] / user_df['Price'][j - 1])) ** 2
        else:
            diff = 0
        total = total + diff
    vol = (sqrt(365 * (total / (step - 1))))
    return vol

def populate_directory(user_df, user_directory, option_lengths):

    for length in option_lengths:
        title = header_label(length)
        vol_mean = title + '-Vol-Mean'
        vol_no_mean = title + '-Vol-No-Mean'
        headers = ['Date', 'Price', title, vol_mean, vol_no_mean]
        d = OrderedDict.fromkeys(headers, [])
        df = pd.DataFrame.from_dict(d)

        d = {}
        for index, series in user_df.iterrows():
            for title in headers:
                d.update({title: user_df[title][index]})
            df = df.append(d, ignore_index=True)

        doc_title = header_label(length) + '.csv'
        csv_location = user_directory / doc_title
        df.to_csv(csv_location)
    return


if __name__ == '__main__':

    # Hardcoded information
    test_u_i = {'Name': '1-BTC', 'Date Format': 'mm-dd-yyyy', 'Start': '1/1/18', 'End': '5/10/18',
                'Trading': 'Mo-Tu-We-Th-Fr'}
    OLs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 30, 60, 90, 120, 150]
    SPs = [90, 95, 100, 105, 110]
    CSs = ['Wide', 'Normal', 'Narrow']
    TSs = {'Calls': [], 'Puts': [], 'Straddles': [], 'Calendar-Spreads': CSs}
    test_a_c = {'Option Lengths': OLs, 'Strikes': SPs, 'Strategies': TSs, 'Granularity': '2'}

    # Initialize User Directory
    user_directory = Path('data') / test_u_i['Name']
    file_name = 'historical' + '.csv'
    user_csv = user_directory / file_name

    # Initialize Option Lengths
    option_lengths = test_a_c['Option Lengths']

    # TO-DO: Trim Unfeasible Option Lengths

    # Standardize Dates
    start = adjust_string(test_u_i['Start'], len(test_u_i['Start']))
    end = adjust_string(test_u_i['End'], len(test_u_i['End']))

    # Read User Data
    user_df = pd.read_csv(user_csv)

    # Validate the Start and End Dates, Move to nearest Monday's and Friday's if necessary
    start = validate_date(user_df, start, 0)
    end = validate_date(user_df, end, 1)

    # TO-DO: Standardizing Arbitrary Date Formats

    # Adjust User df to fit start and end indices
    user_df = fit_dates(user_df, start, end)
    user_length = len(user_df)

    # Identify which LIBOR Rates need to be appended
    libor_lengths = select_LIBOR(option_lengths)
    print(libor_lengths)

    # Read LIBOR Data
    LIBOR_df = pd.read_csv('LIBOR.csv', usecols=libor_lengths)

    # Adjust LIBOR df to fit start and end indices
    LIBOR_df = fit_dates(LIBOR_df, start, end)

    # Initialize Trading Timeline
    trading = test_u_i['Trading']

    # Extend to 7 Day Data, if necessary
    if trading == 'Mo-Tu-We-Th-Fr-Sa-Su':
        # Extend to 7 Day
        LIBOR_df = extend_LIBOR(LIBOR_df, libor_lengths, user_length)

    # Compute Synthetic rf Rates Using Bootstrap Method
    rf_rates = synthetic_LIBOR(option_lengths, LIBOR_df)

    # Concatenate df w/ Risk-free Rates
    user_df = pd.concat([user_df, rf_rates], axis=1)

    # TO-DO: Trim to reflect Granularity of Analysis

    # Generate Volatility Measures
    volatilities = volatility_measures(option_lengths, user_df)

    # Concatenate df w/ Volatility Measures
    user_df = pd.concat([user_df, volatilities], axis=1)

    # Generate individual csv's for each Option Length
    populate_directory(user_df, user_directory, option_lengths)

return



