import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from collections import OrderedDict
from math import log, sqrt, e
from scipy.stats import norm

# LIBOR: {(1/2/86): [1M, 3M, 6M, 1Y],  (1/2/87): [2M], (12/1/97): [1W], (1/2/01): [Overnight]}
# user_input = {Name, Date Format, Start Date, End Date, Trading Days)
# analysis_choices = {[list of Option_Lengths], [List of Strike Prices], [List of Trading Strategies]}

# Sorted in ascending order
# Need to create unique directory every time with server (visitor counter)

def handle_user():

    # Hardcoded information to design the architecture
    test_u_i = {'Name': '1-BTC', 'Date Format': 'mm-dd-yyyy', 'Start': '1/1/18', 'End': '5/10/18',
                       'Trading': 'Mo-Tu-We-Th-Fr'}
    OLs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 30, 60, 90, 120, 150]
    SPs = [90, 95, 100, 105, 110]
    CSs = ['Wide', 'Normal', 'Narrow']
    TSs = {'Calls': [], 'Puts': [], 'Straddles': [], 'Calendar-Spreads': CSs}
    test_a_c = {'Option Lengths': OLs, 'Strikes': SPs, 'Strategies': TSs, 'Granularity': '2'}



    #### Module 1: Create Directory w/ all information partitioned into csv's for each Option Length ####

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

    #### Module 2: Conduct Black-Scholes Pricing and Compute Strategy Payoffs ####

    # Initialize Strike Prices & Trading Strategies
    strikes = test_a_c['Strikes']
    strategies = test_a_c['Strategies']

    print('start debugging')

    # # Compute Put and Call Prices across Strike Prices
    # # Needs Debugged
    BS_prices(user_directory, option_lengths, strikes)

    print('Black-Scholes Pricing Finished')
    return

    # Compute Payoffs for each Strategy across User data
    strategy_payoffs(user_directory, option_lengths, strikes, strategies, trading)



    #### Module 3: Generate Payoff Statistics and Produce Vizualizations ####



    #### Module 4: Create .txt file of Analysis and bundle relevant documents into .zip folder ####


    return


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


def BS_prices(user_directory, option_lengths, strikes):
    for length in option_lengths:
        title = header_label(length)
        csv_name = title + '.csv'
        current_file = user_directory / csv_name
        df = pd.read_csv(current_file)

        strike_titles = strikes
        print(strike_titles)

        BS_headers = []
        for spot_ratio in strike_titles:
            strike = str(spot_ratio) + '%-Spot'
            mean_call = strike + '-Vol-Mean-B-S-Call'
            mean_put = strike + '-Vol-Mean-B-S-Put'
            no_mean_call = strike + '-Vol-No-Mean-B-S-Call'
            no_mean_put = strike + '-Vol-No-Mean-B-S-Put'

            BS_headers.append(title)
            BS_headers.append(mean_call)
            BS_headers.append(mean_put)
            BS_headers.append(no_mean_call)
            BS_headers.append(no_mean_put)

        d = OrderedDict.fromkeys(BS_headers, [])
        BS_df = pd.DataFrame.from_dict(d)

        e = {}
        for series, index in df.iterrows():

            count = 0
            strike_count = 0
            BS_data = BS_dict(df, series, length, strikes[strike_count])

            for title in BS_headers:
                if count == 5:
                    count = 0
                    strike_count = strike_count + 1
                    BS_data = BS_dict(df, series, length, strikes[strike_count])

                elif count == 0:
                    e.update({title: BS_strikes(BS_data)})
                elif count == 1:
                    e.update({title: BS_call(BS_data, True)})
                elif count == 2:
                    e.update({title: BS_put(BS_data, True)})
                elif count == 3:
                    e.update({title: BS_call(BS_data, False)})
                elif count == 4:
                    e.update({title: BS_put(BS_data, False)})

                count = count + 1
            BS_df = BS_df.append(e, ignore_index=True)
        df = pd.concat([df, BS_df], axis=1)
        df.to_csv(current_file)

    return

def BS_dict(df, series, length, strike_percentage):

    d = {'strike': '', 'spot': '', 'rf': '', 'd1_mean': 0, 'd2_mean': 0, 'd1_no_mean': 0, 'd2_no_mean': 0,
         'length': length}

    if (length + 3) > series:
        return d

    spot = df['Price'][series]
    ratio = int(strike_percentage) / 100
    strike = spot * ratio
    d.update({'strike': strike, 'spot': spot})

    title = header_label(length)
    v_m = title + '-Vol-Mean'
    v_nm = title + '-Vol-No-Mean'
    rf = df[title][series]
    vol_mean = df[v_m][series]
    vol_no_mean = df[v_nm][series]

    d1_mean = (1 / (vol_mean * sqrt(length))) * (log((1 / ratio)) + (rf + ((vol_mean ** 2) / 2)) * length)
    d2_mean = d1_mean - vol_mean * sqrt(length)
    d1_no_mean = (1 / (vol_no_mean * sqrt(length))) * (log((1 / ratio)) + (rf + ((vol_no_mean ** 2) / 2)) * length)
    d2_no_mean = d1_no_mean - vol_no_mean * sqrt(length)

    d.update({'rf': rf, 'd1_mean': d1_mean, 'd2_mean': d2_mean, 'd1_no_mean': d1_no_mean, 'd2_no_mean': d2_no_mean})
    return d


def BS_strikes(BS_dict):
    strike = BS_dict['strike']
    return strike


def BS_call(BS_dict, vol_w_mean):
    if vol_w_mean is True:
        d1_key = 'd1_mean'
        d2_key = 'd2_mean'
    else:
        d1_key = 'd1_no_mean'
        d2_key = 'd2_no_mean'

    if BS_dict[d1_key] == 0 and BS_dict[d2_key] == 0:
        return ''

    d1 = BS_dict[d1_key]
    d2 = BS_dict[d2_key]
    spot = BS_dict['spot']
    strike = BS_dict['strike']
    rf = BS_dict['rf']
    length = BS_dict['length']

    x = (norm.cdf(d1) * spot) - (norm.cdf(d2) * strike * e ** (-1 * rf * length))
    return x


def BS_put(BS_dict, vol_w_mean):
    if vol_w_mean is True:
        d1_key = 'd1_mean'
        d2_key = 'd2_mean'
    else:
        d1_key = 'd1_no_mean'
        d2_key = 'd2_no_mean'

    if BS_dict[d1_key] == 0 and BS_dict[d2_key] == 0:
        return ''

    d1 = BS_dict[d1_key]
    d2 = BS_dict[d2_key]
    spot = BS_dict['spot']
    strike = BS_dict['strike']
    rf = BS_dict['rf']
    length = BS_dict['length']

    y = (norm.cdf(-1 * d2) * strike * e ** (-1 * rf * length)) - (norm.cdf(-1 * d1) * spot)
    return y


def strategy_payoffs(user_directory, option_lengths, strikes, strategies, trading):

    for length in option_lengths:
        title = header_label(length)
        csv_name = title + '.csv'
        current_file = user_directory / csv_name
        df = pd.read_csv(current_file)
        df = handle_strategies(df, length, strikes, strategies, trading)
        df.to_csv(current_file)

    return

def handle_strategies(df, length, strikes, strategies, trading):

    strike_titles = strikes

    complete_strategies = strategies
    if 'Puts' not in complete_strategies:
        complete_strategies.insert(0, 'Puts')
    if 'Calls' not in complete_strategies:
        complete_strategies.insert(0, 'Calls')


    df_headers = []
    for spot_ratio in strike_titles:
        strike = str(spot_ratio) + '%-Spot'
        df_headers = strategy_headers(complete_strategies, strike)

    d = OrderedDict.fromkeys(df_headers, [])
    strategy_df = pd.DataFrame.from_dict(d)

    for index, series in df.iterrows():
        f = compute_strategies(df, complete_strategies, df_headers, index)
        d.update(f)
        strategy_df = strategy_df.append(d, ignore_index=True)

    new_df = pd.concat([df, strategy_df], axis=1)
    return new_df


def strategy_headers(complete_strategies, strike):
    mean_title = strike + '-Vol-Mean-B-S'
    no_mean_title = strike + '-Vol-No-Mean-B-S'

    headers = []
    for key, value in complete_strategies.items():
        mean_type = mean_title + '-' + key + '-Payoff'
        no_mean_type = no_mean_title + '-' + key + '-Payoff'
        if not value:
            headers.append(mean_type)
            headers.append(no_mean_type)
            continue
        for measure in value:
            mean_method = mean_type + measure + '-Payoff'
            no_mean_method = no_mean_type + measure + '-Payoff'
            headers.append(mean_method)
            headers.append(no_mean_method)
    return headers


def compute_strategies(df, complete_strategies, df_headers, index):

    d = {}
    count = 0
    for method in complete_strategies:
        d.update({method: strategy_map(df, complete_strategies, method, count, index)})
        count = count + 1
    return 0


def map_reference(method):
    if method == 'Calls':
        return 1
    return 0


def strategy_map(df, complete_strategies, title, count, index):

    

    return 0

if __name__ == '__main__':

    handle_user()