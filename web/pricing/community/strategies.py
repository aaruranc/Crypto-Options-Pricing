import pandas as pd
from computations import search_and_compute


def calls(current_file, df, length, strike):

    pd.DataFrame(columns=['Calls'])
    d = {'Calls': []}

    for index, series in df.iterrows():
        return


def puts():
    return


def bear_spreads(directory, horizon, current_file, df, strike, strategy, method):

    payoff = method + '-P'
    ROI = method + '-ROI'

    if strategy[-1:] == 'A':
        diff = 5
    else:
        diff = 2

    written_strike = strike - diff
    if 95 <= strike <= 105:

        # New Query needs updatees

        new_query = 0
        search_and_compute(new_query)
        long = str(strike) + '-Puts'
        short = str(written_strike) + '-Puts'

    else:
        new_query = 0
        search_and_compute(directory, horizon, written_strike, 'Calls')
        long = str(strike) + '-Calls'
        short = str(written_strike) + '-Calls'

    bear_spread_df = pd.DataFrame(columns=[method, payoff, ROI])

    for index, series in df.iterrows():
        if len(df) < (index + horizon + 1):
            break

        cost = df[long][index] - df[short][index]
        spot = df['Price'][index]
        future_price = df['Price'][index + horizon]
        long_contract = strike * spot
        short_contract = written_strike * spot

        profit = ''
        if long_contract <= future_price:
            profit = 0
        elif short_contract < future_price < long_contract:
            profit = future_price - written_strike
        elif future_price <= short_contract:
            profit = long_contract - short_contract

        returns = profit / cost
        d = {method: cost, payoff: profit, ROI: returns}
        bear_spread_df = bear_spread_df.append(d, ignore_index=True)
    df = pd.concat([df, bear_spread_df], axis=1)
    df.to_csv(current_file)
    return

def bull_spreads():
    return


def box_spreads():
    return


def butterfly_spreads():
    return


def calendar_spreads():
    return


def straddle(current_file, df, method):

    payoff = method + '-P'
    ROI = method + '-ROI'

    straddle_df = pd.DataFrame(columns=[method, payoff, ROI])

    c = str(strike) + '-Calls'
    cp = c + '-P'
    p = str(strike) + '-Puts'
    pp = c + '-P'

    for index, series in df.iterrows():

        cost = df[c][index] + df[p][index]
        profit = df[cp][index] + df[pp][index]
        returns = payoff / cost

        d = {method: cost, payoff: profit, ROI: returns}
        straddle_df = straddle_df.append(d, ignore_index=True)

    df = pd.concat([df, straddle_df], axis=1)
    df.to_csv(current_file)

    return


def strangle():
    return


def strap():
    return


def strip():
    return