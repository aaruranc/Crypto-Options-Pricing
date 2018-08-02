import sys
import os
from pathlib import Path
import pandas as pd
# from options_pricer import driver1
from normalize_date import standardize_date, start_date
from price_history import price_movements
from risk_free import interest_rates
from CCI30 import index_vals

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

    # Append Movements & Volatilities for 1,2,3,5,6,7,8,9,10,11,12,13,14-Day & 1,2,3,6,12-Months & 1,1.5,2-Years
    print('Calculating Price Movements and Volatilities...')
    step_2 = price_movements(step_1, start)
    print('Price Movements and Volatilities Have Been Appended')

    # Append Interest Rates for 1,3 and 6-Month & 11 and 2-Year U.S. Treasury Bills
    print('Appending Historical Interest Rates...')

    step_3 = interest_rates(step_2, start)
    print('Interest Rates Have Been Appended')

    # Append CCI30 Data
    print('Appending CCI30 Index...')
    step_4 = index_vals(step_3, start)
    print('CCI30 Index Appended')
    print(step_4)

    # Generate New csv
    print('Generating New .csv File...')
    newDir = Path('pricing') / asset
    newCSV = newDir / 'historical.csv'
    os.makedirs(newDir)
    step_4.to_csv(newCSV)
    print('New .csv File Generated')
    print('File is located at:')
    print(newCSV)
    next_command = 'Use next driver w/ command: python driver2.py' + ' ' + asset
    print(next_command)

