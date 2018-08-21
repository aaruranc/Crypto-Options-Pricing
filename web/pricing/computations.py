from pathlib import Path
import os
import pandas as pd
from math import sqrt, log, e, ceil
from community import strategies
from scipy.stats import norm


# def str_adjust(date):
#     length = len(date)
#     if length == 6:
#         new_date = "0" + date[0:2] + "0" + date[2:]
#         return  new_date
#     if length == 7:
#         if date[1] == "/":
#             new_date = "0" + date
#             return new_date
#         else:
#             new_date = date[0:3] + "0" + date[3:]
#             return new_date
#     if length == 8:
#         return date

def option_payoff(a, b, d, df, title, index):
    n = len(df)




    return


def option_price(a, d1, d2, parameters):
    m = parameters['spot']
    n = parameters['strike']
    o = parameters['rf']
    p = parameters['length']

    if a == 'Calls':
        x = (norm.cdf(d1) * m) - (norm.cdf(d2) * n * (e ** (-1 * o * p)))
    elif a == 'Puts':
        x = (norm.cdf(-1 * d2) * n * (e ** (-1 * o * p))) - (norm.cdf(-1 * d1) * m)
    return x



def BS_option_calcs(df, parameters, title, index):

    options = ['Calls', 'Puts']
    volatilities = ['VM', 'VNM']
    type = ['Price', 'Payoff', 'ROI']

    d = {}
    for a in options:
        for b in volatilities:
            if b == 'VM':
                d1 = parameters['d1_mean']
                d2 = parameters['d2_mean']
            else:
                d1 = parameters['d1_no_mean']
                d2 = parameters['d2_no_mean']
            for c in type:
                if c == 'Price':
                    x = option_price(a, d1, d2, parameters)
                elif c == 'Payoff':
                    x = option_payoff(a, b, d, df, title, index)
                else:
                    x = d[a][b]['Payoff'] / d[a][b]['Price']


                d.update({a: {b : {c: x}}})


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
    d.update({'rf': risk_free})
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
        data = BS_option_calcs(df, parameters, title, index)

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

    if shorter:
        vals = df['VIX-Close'].tolist()
        counter = 0
        while (len(vals) < date_length):
            x = int(((counter + 1) * stepsize) + counter)
            if x > len(vals):
                vals.append(vals[len(vals) - 1])
            else:
                vals.insert(x, vals[x-1])
            counter = counter + 1
        d = {'VIX': vals}
        df = pd. DataFrame.from_dict(d)

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

    trading_strategy = query['trading_strategy']
    length = int(query['option_length'])
    strike = query['strike']
    current_directory = Path(query['current_directory'])
    source = Path(query['source'])

    option_length = option_label(length)
    loc = option_length + '.csv'
    query_file = current_directory / loc
    print(query_file)

    if os.path.isfile(query_file):
        # df = pd.read_csv(query_file)
        # headers = list(df)
        # strike_str = str(strike)
        # if strike_str in headers:
        #     method = strike_str + '-' + trading_strategy
        #     if method in headers:
        #         return
        #     else:
        #         handle_strategy(current_directory, query_file, df, length, strike, trading_strategy)
        #         return
        #
        # else:
        #     new_strike_data(query_file, df, length, strike)
        #     handle_strategy(current_directory, query_file, df, length, strike, trading_strategy)
            return

    else:
        df = pd.read_csv(source)
        dates = find_dates(df)
        date_length = len(df['Datetime'])
        VIX = grab_data(dates)
        updated_VIX = fix_length(VIX, date_length)
        LIBOR = grab_data(dates, length=length)
        updated_LIBOR = fix_length(LIBOR, date_length, title=option_length)
        vols = calc_volatilities(df, length)
        df = pd.concat([df, updated_VIX, updated_LIBOR, vols], axis=1)
        print(df)

        # new_strike_data(query_file, df, length, strike)

        df.to_csv(query_file, index=False)

        return

if __name__ == '__main__':
    print('computations main executed')

    test_query = {'trading_strategy': 'Calls', 'option_length': '3', 'strike': '90',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv'}

    search_and_compute(test_query)