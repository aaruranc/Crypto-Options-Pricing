import pandas as pd
from math import e, isnan, log, sqrt
from pathlib import Path
import sys
import os
from collections import OrderedDict
from scipy.stats import norm
import numpy as np


def bs_call(spot, strike, rf_rate, vol, length):

    rf_rate = np.float64(rf_rate)
    length = np.float64(length)
    # print(type(spot))
    # print(type(strike))
    # print(type(rf_rate))
    # print(type(vol))
    # print(type(length))

    d1 = (1 / (vol * sqrt(length))) * (log((strike/spot) + (rf_rate + ((vol ** 2) / 2) * length)))
    d2 = d1 - vol * sqrt(length)
    price = (norm.cdf(d1) * spot) - ((norm.cdf(d2)) * (strike * (e ** (-1 ** rf_rate * length))))
    return price


def bs_put(spot, strike, rf_rate, vol, length):

    rf_rate = np.float64(rf_rate)
    length = np.float64(length)

    d1 = (1 / (vol * sqrt(length))) * (log((strike/spot) + (rf_rate + ((vol ** 2) / 2) * length)))
    d2 = d1 - vol * sqrt(length)
    price = ((norm.cdf(-1 * d2)) * (strike * (e ** (-1 ** rf_rate * length)))) - (norm.cdf(-1 * d1) * spot)
    return price


def put_call_premiums(option_length_df, option_length):

    rf_timeline = ''
    if option_length <= 30:
        rf_timeline = '1 Month Treasury Bill'

    v_w_m_header = []
    v_w_o_m_header = []

    tags = list(option_length_df.columns)

    position = 0
    for name in tags:
        if position == 4:
            v_w_m_header = name
        if position == 5:
            v_w_o_m_header = name
            break
        position = position + 1

    strike_vals = []
    for k in range(90, 111, 10):
        strike_vals.append(k)

    strike_headers = []
    for spot_ratio in strike_vals:
        strike = str(spot_ratio) + '%' + ' ' + 'Spot'
        strike_headers.append(strike)

    strikes = OrderedDict.fromkeys(strike_headers, [])
    df = pd.DataFrame.from_dict(strikes)
    d = {}

    for series, index in option_length_df.iterrows():
        count = 0
        for title in strike_headers:
            d.update({title: (option_length_df['Price'][series] * (strike_vals[count] / 100))})
            count = count + 1
        df = df.append(d, ignore_index=True)

    q_df = pd.concat([option_length_df, df], axis=1)

    premium_headers = []
    for spot_ratio in strike_vals:
        call_w_mean = str(spot_ratio) + '%' + ' ' + 'Call Price (Vol w/ Mean)'
        put_w_mean = str(spot_ratio) + '%' + ' ' + 'Put Price (Vol w/ Mean)'
        call_w_o_mean = str(spot_ratio) + '%' + ' ' + 'Call Price (Vol w/o Mean)'
        put_w_o_mean = str(spot_ratio) + '%' + ' ' + 'Put Price (Vol w/o Mean)'

        premium_headers.append(call_w_mean)
        premium_headers.append(put_w_mean)
        premium_headers.append(call_w_o_mean)
        premium_headers.append(put_w_o_mean)

    premiums = OrderedDict.fromkeys(premium_headers, [])
    m_df = pd.DataFrame.from_dict(premiums)
    e = {}

    for series, index in option_length_df.iterrows():
        spot = q_df['Price'][series]
        rf_rate = q_df[rf_timeline][series]
        vol_w_mean = q_df[v_w_m_header][series]
        vol_w_o_mean = q_df[v_w_o_m_header][series]


        if rf_rate == '.':
            rf_rate = q_df[rf_timeline][series-1]
            if rf_rate == '.':
                rf_rate = q_df[rf_timeline][series-2]
                if rf_rate == '.':
                    rf_rate = q_df[rf_timeline][series-3]

        spot_count = 0
        temp_count = 0
        for title in premium_headers:

            if temp_count == 4:
                temp_count = 0
                spot_count = spot_count + 1

            if title[-7] == '/':

                if title[5] == 'C' or title[5] == 'a':
                    strike = q_df[strike_headers[spot_count]][series]
                    price = bs_call(spot, strike, rf_rate, vol_w_mean, option_length)
                    e.update({title: price})

                else:
                    strike = q_df[strike_headers[spot_count]][series]
                    price = bs_put(spot, strike, rf_rate, vol_w_mean, option_length)
                    e.update({title: price})

            else:

                if title[5] == 'C' or title[5] == 'a':
                    strike = q_df[strike_headers[spot_count]][series]
                    price = bs_call(spot, strike, rf_rate, vol_w_o_mean, option_length)
                    e.update({title: price})
                else:
                    strike = q_df[strike_headers[spot_count]][series]
                    price = bs_put(spot, strike, rf_rate, vol_w_o_mean, option_length)
                    e.update({title: price})
            temp_count = temp_count + 1

        m_df = m_df.append(e, ignore_index=True)

    f_df = pd.concat([q_df, m_df], axis=1)

    print(f_df)

    return f_df



def create_csv(asset, BS_premiums_df, option_length):
    if option_length <= 14:
        title = str(option_length) + '_day'

    if 14 < option_length < 365:
        month = option_length // 30
        title = str(month) + '_month'

    if option_length >= 365:
        year = option_length // 365
        title = str(year) + '_year'

    # Need to make directory, solve repeat name problem
    # location = Path('pricing') / asset / 'black_scholes' / title / 'premiums.csv'
    # BS_premiums_df.to_csv(location)
    return


if __name__ == '__main__':
    a = 0
    b = 0
    put_call_premiums(a, b)