import pandas as pd
from math import log, sqrt, exp
from scipy.stats import norm


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

    if vol == 0:
        return 1000

    return (log(ratio) + (length * (rf + ((vol ** 2) / 2)))) / (vol * sqrt(length))


def option_label(length):

    if int(length) < 15:
        option_length = str(length) + '-Day'
    elif 14 < int(length) < 365:
        num = int(length) // 30
        option_length = str(num) + '-Month'
    else:
        option_length = '1-Year'
    return option_length


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
