from pathlib import Path
import os
import pandas as pd
from math import sqrt, log, exp, ceil
from community import strategies
from scipy.stats import norm


def handle_strategy(query, query_file):

    strategy = query['trading_strategy']
    df = pd.read_csv(query_file)

    if strategy == 'Calls':
        return
    elif strategy == 'Puts':
        return
    elif strategy == 'Straddles':
        strategies.straddle(query, query_file)
        return

    ##### Add the rest of the strategies

    return

def option_price(option_type, volatility_type, parameters):

    # if volatility_type == 'VNM':
    #     d1 = parameters['d1_no_mean']
    #     d2 = parameters['d2_no_mean']
    # elif volatility_type == 'VM':
    #     d1 = parameters['d1_mean']
    #     d2 = parameters['d2_mean']

    d1 = parameters['d1']
    d2 = parameters['d2']
    m = parameters['spot']
    n = parameters['strike']
    o = parameters['rf']
    p = parameters['length']

    if option_type == 'Calls':
        x = (norm.cdf(d1) * m) - (norm.cdf(d2) * n * (exp(-o * p)))
    elif option_type == 'Puts':
        x = (norm.cdf(-d2) * n * exp(-1 * o * p)) - (norm.cdf(-d1) * m)

    return x


def BS_option_calcs(parameters):

    options = ['Calls', 'Puts']
    # volatilities = ['VM', 'VNM']

    d = {}
    # for a in options:
    #     e = {}
    #     for b in volatilities:
    #         e.update({b: option_price(a, b, parameters)})
    #     d.update({a: e})
    # d.update({'input': parameters})


    for a in options:
        d.update({a: option_price(a, 0, parameters)})

    return d


def compute_d1(v, l, r, rf):
    # print('Vol')
    # print(v)
    # print('Length')
    # print(l)
    # print('Ratio')
    # print(r)
    # print('Risk Free')
    # print(rf)
    x = (log(r) + ((rf + ((v ** 2) / 2)) * l)) / (v * sqrt(l))
    # print('d1')
    # print(x)
    return x


def compute_d2(d1, v, l):
    y = d1 - (v * sqrt(l))
    # print('d2')
    # print(y)
    # print('__________')
    return y


def BS_dict(df, index, length, percentage):

    year_length = length / 365
    title = option_label(length)
    v_m = title + '-VM'
    # v_nm = title + '-VNM'
    rf_title = title + '-LIBOR'

    ratio = 1 / percentage
    spot = df['Price'][index]
    strike = spot * percentage
    rf = df[rf_title][index]

    # vol_mean = float(df[v_m][index])
    # vol_no_mean = float(df[v_nm][index])

    vol = float(df[v_m][index])
    d1 = compute_d1(vol, year_length, ratio, rf)
    d2 = compute_d2(d1, vol, year_length)

    d = {'index': index, 'length': year_length, 'strike': strike, 'spot': spot, 'ratio': ratio,
         'rf': rf, 'vol': vol, 'd1': d1, 'd2': d2}

    # call = (norm.cdf(d1) * spot) - (norm.cdf(d2) * strike * (e ** (-1 * rf * year_length)))
    # put = (norm.cdf(-1 * d2) * strike * (e ** (-1 * rf * year_length))) - (norm.cdf(-1 * d1) * spot)
    # d.update({'call': call, 'put': put})

    calcs = BS_option_calcs(d)
    d.update({'calc_call': calcs['Calls'], 'calc_put': calcs['Puts']})
    print(d)


    # print('__________')
    # print('Index:')
    # print(index)
    # print('__________')
    # print('Spot')
    # print(spot)
    # print('Strike')
    # print(strike)

    # d1_mean = compute_d1(vol_mean, year_length, ratio, risk_free)
    # d2_mean = compute_d2(d1_mean, vol_mean, year_length)
    # d1_no_mean = compute_d1(vol_no_mean, year_length, ratio, risk_free)
    # d2_no_mean = compute_d2(d1_no_mean, vol_no_mean, year_length)
    #
    # d.update({'d1_mean': d1_mean, 'd2_mean': d2_mean, 'd1_no_mean': d1_no_mean, 'd2_no_mean': d2_no_mean})
    return d


def new_strike_data(query, query_file, df):

    length = int(query['option_length'])
    strike = int(query['strike'])

    title = str(strike)
    c = title + '-Calls'
    p = title + '-Puts'


    ### Need a Datafram Column for Strike Prices

    percentage = strike / 100
    # headers = [(c + '-VM'), (c + '-VNM'), (p + '-VM'), (p + '-VNM')]
    headers = [c, p]
    options_df = pd.DataFrame(columns=headers)
    d = {}
    size = len(df)

    for index, series in df.iterrows():
        if length + 1 > index or size < (index + length):
            # d.update({(c + '-VM'): '',
            #           (c + '-VNM'): '',
            #           (p + '-VM'): '',
            #           (p + '-VNM'): ''
            #           })
            d.update({c: '', p: ''})
        else:
            parameters = BS_dict(df, index, length, percentage)
            data = BS_option_calcs(parameters)
            d.update({c: data['Calls'], p: data['Puts']})

            # d.update({(c + '-VM'): data['Calls']['VM'],
            #           (c + '-VNM'): data['Calls']['VNM'],
            #           (p + '-VM'): data['Puts']['VM'],
            #           (p + '-VNM'): data['Puts']['VNM']
            #           })

        options_df = options_df.append(d, ignore_index=True)

    updated_df = pd.concat([df, options_df], axis=1)
    print(updated_df)
    updated_df.to_csv(query_file)
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
    vol = 16 * (sqrt(total / (length-1))) * 100
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
    vol = (sqrt(256 * (total / (length - 1)))) * 100
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

    length = int(query['option_length'])
    current_directory = Path(query['current_directory'])
    source = Path(query['source'])
    strike = query['strike']
    strategy = query['trading_strategy']

    option_length = option_label(length)
    loc = option_length + '.csv'
    query_file = current_directory / loc

    if os.path.isfile(query_file):
        df = pd.read_csv(query_file)
        headers = list(df)
        test = strike + '-Calls'
        if test in headers:
            method = strike + '-' + strategy
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
        df = pd.read_csv(source)

        dates = find_dates(df)
        date_length = len(df['Datetime'])

        VIX = grab_data(dates)
        updated_VIX = fix_length(VIX, date_length)

        LIBOR = grab_data(dates, length=length)
        updated_LIBOR = fix_length(LIBOR, date_length, title=option_length)

        vols = calc_volatilities(df, length)

        df = pd.concat([df, updated_VIX, updated_LIBOR, vols], axis=1)

        new_strike_data(query, query_file, df)
        handle_strategy(query, query_file)

        return

if __name__ == '__main__':
    print('computations main executed')

    test_query = {'trading_strategy': 'Calls', 'option_length': '9', 'strike': '110',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv'}

    # loc = Path(test_query['current_directory']) / '9-Day.csv'
    # df = pd.read_csv(loc)
    # new_strike_data(loc, df, test_query)

    annual_rf = (1.121521739) ** (365 / 9)

    x = {'i': 1390, 'l': 0.024657534246575342, 'st': 78.66573000000001, 'sp': 71.5143,
         'r': 0.9090909090909091, 'rf': 1.121521739, 'v': 48.10019478494585, 'd1': 3.764296825178816,
         'd2': -3.7887409643280927, 'c': 71.50239022171021, 'p': 78.41845694879935}

    # d1 = 3.764296825178816
    # d2 = -3.7887409643280927
    # n_d1 = 0.9999164907998107
    # n_d2 = 7.570634363292039e-05

    calc_call = 71.50239022171021
    calc_put = 8.41845694879935

    web_call = .28 / .29
    web_put = 7.3 / 7.4

    # j = norm.ppf(.1118)
    # k = -norm.ppf(.8882)
    # l = norm.ppf((.0214 / (x['spot'] * sqrt(x['length']))) * exp(x['rf'] * x['length']))
    # temp = (.0352 * x['spot'] * sqrt(x['length']) * x['vol'])
    # print(temp)
    # m = norm.ppf(temp)
    # y = (j + k + l + m) / 4
    # print('d1')
    # print(j, k, l, m)
    # print(y)
    #
    # a = norm.ppf((.0019 / (x['strike'] * x['length'])) * exp(x['rf'] * x['length']))
    # b = -norm.ppf((.00175 / (x['strike'] * x['length'])) * exp(x['rf'] * x['length']))
    # c = norm.ppf((.0214 / (x['strike'] * sqrt(x['length']))) * exp(x['rf'] * x['length']))
    # d = norm.ppf(exp(x['rf'] * x['length']) * ((.0214 / (x['strike'] * sqrt(x['length']))) * exp(x['rf'] * x['length'])) / x['strike'])
    # z = (a + b + c + d) / 4
    # print('d2')
    # print(a, b, c, d)
    # print(z)

    # d1 = -1.217011
    # d2 = -3.095

    delta = .1107
    rho = .0019
    d1 = norm.ppf(delta)
    d2 = norm.ppf((rho / (x['st'] * x['l'])) * exp(x['rf'] * x['l']))


    c = x['sp'] * norm.cdf(d1) - (x['st'] * exp(-1 * x['rf'] * x['l']) * norm.cdf(d2))
    p = (x['st'] * exp(-1 * x['rf'] * x['l']) * norm.cdf(-d2)) - x['sp'] * norm.cdf(-d1)

    print(c)
    print(p)


    # search_and_compute(test_query)