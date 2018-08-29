import sys
import os
import pandas as pd
from pathlib import Path
from black_scholes import put_call_premiums, create_csv

if __name__ == '__main__':
    asset = sys.argv[1]
    assetCSV = Path('pricing') / asset / 'historical.csv'
    print(assetCSV)
    date_n_price_cols = [1, 2]

    all_data = pd.read_csv(assetCSV)
    df = pd.read_csv(assetCSV, usecols=date_n_price_cols)

    dffs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 30, 60, 90, 120, 150, 180, 365, 730]
    strategies = []

    header_tags = list(all_data.columns)

    rf_CAPM_headers = []
    for j in range(-9, 0):
        rf_CAPM_headers.append(header_tags[j])

    rf_CAPM = all_data[rf_CAPM_headers]
    # print(rf_CAPM)

    # Compute and Store Call and Put Premiums for Vanilla Black-Scholes
    column_count = 7
    for option_length in dffs:
        if option_length == 2:
            break

        option_length_df = df

        for j in range(column_count, column_count + 4):
            option_length_df = pd.concat([option_length_df, all_data[header_tags[j]]], axis=1)
        option_length_df = pd.concat([option_length_df, rf_CAPM], axis=1)

        option_length = 2

        # Compute Premiums
        BS_premiums = put_call_premiums(option_length_df, option_length)

        # create_csv(asset, BS_premiums_df, option_length)

        column_count +=4



    # Compute Payoffs for Calls, Puts, Straddles, Strangles and Spreads


