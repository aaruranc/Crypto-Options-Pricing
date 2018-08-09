from pathlib import Path
import pandas as pd
import json
import time


def price_JSON():

    print('executed')
    # current_file = Path(current_directory) / 'historical.csv'
    hardcode = Path('data/AAPL.csv')

    df = pd.DataFrame.read_csv(hardcode)
    a = []
    for index, series in df.iterrows():
        a.append({df['Date'][index]: df['Price'][index]})

    df_length = len(a)
    data = {'length': df_length, 'data': a}
    print(json.JSONEncoder(data))

    return


def volatility_JSON(df):

    a = []
    for index, series in df.iterrows():
        k = {'Vol-Mean': df['Vol-Mean'][index], 'Vol-No-Mean': df['Vol-No-Mean'][index]}
        p = {df['Date'][index]: k}
        a.append(p)

    df_length = len(a)
    d = {'length': df_length, 'data': a}
    return d

def strategy_JSON(df, method):

    a = []
    for index, series in df.iterrows():
        k = {'Price': df['Price'][index], 'Strategy-Cost': df[method][index]}
        p = {df['Date'][index]: k}
        a.append(p)

    df_length = len(a)
    d = {'length': df_length, 'data': a}
    return d


def ROI_JSON(df, option_length, method):

    a = []
    rf_rates = option_length + '-LIBOR'
    returns = method + '-ROI'

    for index, series in df.iterrows():
        k = {'LIBOR': df[rf_rates][index], 'ROI': df[returns][index]}
        p = {df['Date'][index]: k}
        a.append(p)

    df_length = len(a)
    d = {'length': df_length, 'data': a}
    return d


def distribution_JSON(df, method):
    num_buckets = 50
    return 0

def query_to_JSON():
    return


def hardcode():
    # Hardcoded Information
    d = {'strategy': 'Calls', 'length': 1, 'strike': 90, 'user_directory': Path('data/AAPL'), 'granularity': '5'}

    directory = d['user_directory']
    horizon = d['length']
    strike = d['strike']
    strategy = d['strategy']
    method = str(strike) + '-' + strategy

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

    df = pd.DataFrame.read_csv(current_file)

    # Asset Price Evolution
    price_evolution = price_JSON(df)

    # Volatility Evolution
    volatility_evolution = volatility_JSON(df)

    # Strategy Payoff Diagram

    # Strategy Price Evolution
    strategy_evolution = strategy_JSON(df, option_length, method)

    # Day to Day ROI
    ROI_evolution = ROI_JSON(df, method)

    # Distribution of Payoffs
    payoff_distribution = distribution_JSON(df, method)

    data = {'Price Evolution': price_evolution, 'Volatility Evolution': volatility_evolution,
            'Strategy Evolution': strategy_evolution, 'ROI Evolution': ROI_evolution,
            'Distribution': payoff_distribution}

    id = str(int(time.time())) + '.txt'
    json_loc = current_directory / id

    with open(json_loc, 'w') as outfile:
        json.dump(data, outfile)
    return


if __name__ == '__main__':
    print('main executed')
    price_JSON()
