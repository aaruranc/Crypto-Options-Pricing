from pathlib import Path
import os
import pandas as pd
from math import sqrt, log
import strategies


def str_adjust(date):
    length = len(date)
    if length == 6:
        new_date = "0" + date[0:2] + "0" + date[2:]
        return  new_date
    if length == 7:
        if date[1] == "/":
            new_date = "0" + date
            return new_date
        else:
            new_date = date[0:3] + "0" + date[3:]
            return new_date
    if length == 8:
        return date


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
        strategies.calls()
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


def volatility_mean(df, length, index):
    if length == 1:
        return ''
    if index < (length+1):
        return ''
    sum = 0
    for i in range((index - length), index):
        log_return = log(df['Price'][i] / df['Price'][i-1])
        sum = sum + log_return
    mu = sum / length
    total = 0
    for j in range((index - length), index):
        diff = (log(df['Price'][j] / df['Price'][j-1]) - mu) ** 2
        total = total + diff
    vol = 16 * (sqrt(total / (length-1)))
    return vol


def volatility_no_mean(df, length, index):
    if length == 1:
        if index >= 1:
            log_return = log(df['Price'][index] / df['Price'][index - 1])
            vol = 16 * (log_return ** 2)
            return vol

    if index < (length+1):
        return ''

    total = 0
    for j in range((index - length), index):
        diff = (log(df['Price'][j] / df['Price'][j - 1])) ** 2
        total = total + diff
    vol = (sqrt(256 * (total / (length - 1))))
    return vol


def volatility_dict(df, length, index, mean_title, no_mean_title):
    vm = volatility_mean(df, length, index)
    vnm = volatility_no_mean(df, length, index)

    d = {mean_title: vm, no_mean_title: vnm}
    return d


def calc_volatilities(df, length):

    title = option_label(length)
    mean_title = title + '-VM'
    no_mean_title = title + '-VNM'
    vol_df = pd.DataFrame(columns=[mean_title, no_mean_title])
    d = {mean_title: [], no_mean_title: []}

    for index, series in df.iterrows():
        if index < length:
            d.update({mean_title: '', no_mean_title: ''})
        else:
            d.update(volatility_dict(df, length, index, mean_title, no_mean_title))
        vol_df = vol_df.append(d, ignore_index=True)
    return vol_df


def grab_data(dates, length=0):
    if length == 0:
        df = pd.read_csv('VIX.csv', usecols=['Date', 'VIX-Close'])
        vals = pd.read_csv('VIX.csv', usecols=['VIX-Close'])
        start = str_adjust(dates['start'])
        end = str_adjust(dates['end'])
    else:
        header = option_label(length) + '-LIBOR'
        df = pd.read_csv('LIBOR.csv', usecols=['Date', header])
        vals = pd.read_csv('LIBOR.csv', usecols=[header])
        start = dates['start']
        end = dates['end']

    started = False
    start_index = 0
    end_index = 0
    for index, series in df.iterrows():
        if not started:
            if df['Date'][index] == start or str_adjust(df['Date'][index]) == start:
                print(df['Date'][index])
                started = True
                start_index = index
            continue
        if started:
            if df['Date'][index] == end or str_adjust(df['Date'][index]) == end:
                print('executed')
                print(df['Date'][index])
                end_index = index
                break
            continue
    print(start)
    print(start_index)
    print(end)
    print(end_index)

    data = (df.loc[start_index:end_index]).copy()
    data.reset_index(drop=True, inplace=True)
    return data


def find_dates(df):

    n = len(df)
    e = n - 3
    start_date = df['Date'][0]
    end_date = df['Date'][e]
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

    trading_strategy = query['trading_strategy']
    length = int(query['option_length'])
    strike = query['strike']
    current_directory = Path(query['current_directory'])
    source = Path(query['source'])

    option_length = option_label(length)

    loc = option_length + '.csv'
    query_file = current_directory / loc
    print(loc)
    print(query_file)

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
        print(df)
        dates = find_dates(df)
        print(dates)
        VIX = grab_data(dates)
        print(VIX)
        LIBOR = grab_data(dates, length)
        print(LIBOR)
        vols = calc_volatilities(df, length)
        print(vols)

        a = len(df)
        b = len(VIX)
        c = len(LIBOR)

        if b <= c:
            if a <= b:
                VIX = VIX.loc[:a]
                LIBOR = LIBOR.loc[:a-1]
            else:
                df = df.loc[:b]
                LIBOR = LIBOR.loc[:b]
        else:
            if a <= c:
                VIX = VIX.loc[:a]
                LIBOR = LIBOR.loc[:a]
            else:
                df = df.loc[:c]
                LIBOR = LIBOR.loc[:c]

        df = pd.concat([df, vols], axis=1)
        df_2 = pd.concat([VIX, LIBOR], axis=1)
        print(df)
        print(df_2)

        return

        # k = len(rf_rates)
        # for index, series in df.iterrows():
        #     count = 0
        #     for index_2, series_2 in rf_rates.iterrows():
        #         if index == index_2:
        #             print(df['Date'][index])

                # if df['Date'][index] == rf_rates['Date'][index_2]:
                #     # print(index)
                #     # print(df['Date'][index])
                #     # print(index_2)
                #     # print(rf_rates['Date'][index_2])
                #     # print('_____')
                #     # print('FOUND')
                #     break
                # elif index_2 == k-1:
                #     print(df['Date'][index])
                #     count = count + 1


        # if rf_rates['Date'][index] != df['Date'][index]:
        #     print(index)
        #     print(rf_rates['Date'][index])



        return
        # df = pd.concat([df, BS_df], axis=1)

        # handle_strategy(current_directory, query_file, df, length, strike, trading_strategy)
        # return


def check_dates():
    LIBOR = pd.read_csv('LIBOR.csv', usecols=['Date'])
    VIX = pd.read_csv('VIX.csv', usecols=['Date'])

    print('LIBOR')

    length = len(LIBOR)
    q = length // 4
    h = length // 2
    t = q * 3

    for index, series in LIBOR.iterrows():

        if index == q:
            print('1/4 Done')
        elif index == h:
            print('1/2 Done')
        elif index == t:
            print('3/4 Done')

        length = len(LIBOR)
        date = LIBOR['Date'][index]
        found = False
        for k in range(index+1, length):
            if LIBOR['Date'][k] == date:
                found = True
                break
        if found:
            print(date)
    print('______________')

    length = len(LIBOR)
    q = length // 4
    h = length // 2
    t = q * 3

    print('VIX')
    for index, series in VIX.iterrows():

        if index == q:
            print('1/4 Done')
        elif index == h:
            print('1/2 Done')
        elif index == t:
            print('3/4 Done')

        length = len(VIX)
        date = LIBOR['Date'][index]
        found = False
        for k in range(index, length-index):
            if VIX['Date'][k] == date:
                found = True
        if found:
            print(date)
    print('______________')

    return


if __name__ == '__main__':
    print('computations main executed')

    test_query = {'trading_strategy': 'Calls', 'option_length': '12', 'strike': '90',
                  'current_directory': 'data/1534366837', 'source': 'data/1534366837/BTC.csv'}
    # search_and_compute(test_query)
    check_dates()