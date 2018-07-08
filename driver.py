import sys
# import matlab.engine
import csv
import datetime
from pathlib import Path
from one_year_price_movements import price_movements
from risk_free_rates import interest_rates

if __name__ == '__main__':
    asset = sys.argv[1]
    asset = asset + '.csv'
    assetCSV = Path('master_prices') / asset

    # # Standardize dateTime
    # dateTime(assetCSV)
    #
    # # Append Price Movements for 1,2,7 and 14-Day & 1,2,6 and 12-Months
    # price_movements(assetCSV)
    # # Append Interest Rates
    # interest_rates(assetCSV)
    # Append CCI30 Prices
    CCI30(assetCSV)

    # Append Deterministic Volatility Measures

    # Run Black-Scholes Against Each Measure

    # Compute Call and Put Option Payoffs

    # Compute Option Strategy Payoffs

    # Push to Matlab to Generate Histograms

    # Generate Continuous Functions from Histograms

    # Generate Basic Statistics

    # Compress into Meta-Statistics for Currency Evaluation

    # Automated Graph Selection

    # Push textdoc and Graphs to User


