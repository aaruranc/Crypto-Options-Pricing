import sys
# import matlab.engine
import csv
import pandas as pd
from pathlib import Path
from date import standardize_date, start_date
from price_history import price_movements
from risk_free import interest_rates
# from deterministic_volatility import volatilities

if __name__ == '__main__':
    asset = sys.argv[1]
    assetCSV = Path('master_prices') / (asset + '.csv')

    # Standardize dateTime
    print('Standardizing Dates...')
    step_1 = standardize_date(assetCSV)
    print('Dates have Been Standardized')
    # Start
    start = start_date(assetCSV)
    print(asset + ' ' + 'Start Date is:')
    print(start)
    # Append Price Movements for 1,2,3,5,6,7,8,9,10,11,12,13 and 14-Day & 1,2,3,6 and 12-Months & 1, 1.5, and 2-Years
    print('Calculating Price Movements...')
    step_2 = price_movements(step_1)
    print('Price Movements Have Been Appended')
    # Append Interest Rates
    print('Appending Historical Interest Rates')
    step_3 = interest_rates(step_2)
    print(step_3)
    print('Interest Rates Have Been Appended')
    # Append CCI30 Prices
    # step_4 = CCI30(step_3)
    #
    # # Append Deterministic Volatility Measures
    # step_5 = volatilities(step_4)
    #
    # # Generate New csv
    # newCSV = Path('pricing') / asset / 'historical.csv'
    # step_5.to_csv(newCSV)

