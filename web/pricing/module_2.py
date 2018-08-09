from pathlib import Path
import os
import pandas as pd


def bull_spreads():
    return

def bear_spreads(directory, horizon, current_file, df, strike, strategy, method, payoff, ROI):

    if strategy[-1:] == 'A':
        diff = 5
    else:
        diff = 2

    written_strike = strike - diff
    if 95 <= strike <= 105:
        search_and_compute(directory, horizon, written_strike, 'Puts')
        long = str(strike) + '-Puts'
        short = str(written_strike) + '-Puts'

    else:
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

def box_spreads():
    return

def butterfly_spreads():
    return

def calendar_spreads():
    return

def straddle(current_file, df, method, payoff, ROI):

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


def handle_strategy(directory, horizon, current_file, df, strike, strategy):

    name = strategy[:-2]
    method = str(strike) + '-' + strategy
    payoff = method + '-P'
    ROI = method + '-ROI'
    if strategy == 'Calls':
        return
    elif strategy == 'Puts':
        return
    elif strategy == 'Straddles':
        straddle(current_file, df, method, payoff, ROI)
        return
    elif name == 'Bear-Spreads':
        bear_spreads(directory, horizon, current_file, df, strike, strategy, method, payoff, ROI)
        return

    return 0


def search_and_compute(directory, horizon, strike, strategy):

    option_length = ''
    if horizon <= 14:
        option_length = horizon + '-Day'
    elif 14 < horizon < 365:
        num = horizon // 30
        option_length = str(num) + '-Month'
    elif horizon == 365:
        option_length = '1-Year'

    loc = option_length + '.csv'
    current_directory = directory / option_length
    current_file = current_directory / loc

    if os.path.isdir(current_directory):
        df = pd.read_csv(current_file)
        headers = list(df)
        strike_str = str(strike)
        if strike_str in headers:
            method = strike_str + '-' + strategy
            if method in headers:
                return
            else:
                handle_strategy(directory, horizon, current_file, df, strike, strategy)
                return

        else:
            # Append New Strike
            handle_strategy(directory, horizon, current_file, df, strike, strategy)
            return

    else:
        df = 0
        # Create Directory
        # Create File
        # Append Data (up to Call/Put Payoffs)
        handle_strategy(directory, horizon, current_file, df, strike, strategy)
        return


if __name__ == '__main__':
    print("hello")
    print('module_2 executed')

    d = {'trading_strategy': 'Calls', 'length': 1, 'strike': 90, 'user_directory': Path('data/AAPL'), 'granularity': '5'}

    directory = d['user_directory']
    horizon = d['length']
    strike = d['strike']
    strategy = d['trading_strategy']


    # Checks if data is available, updates csv if not
    # search_and_compute(directory, horizon, strike, strategy)

    # Asset Price Evolution

    # Volatility Evolution

    # Strategy Payoff Diagram

    # Strategy Price Evolution

    # Distribution of Payoffs

    # Day to Day ROI