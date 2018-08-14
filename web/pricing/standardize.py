from pathlib import Path
import pandas as pd

if __name__ == '__main__':

    loc = Path('data/AAPL')
    d = {'asset': 'AAPL', 'format': 'mm-dd-yyyy', 'start': '01/01/0000', 'end': '12/31/10', 'trading': 'weekdays',
         'user_directory': loc}

    # Verify Start End and Contiguity of Data
    file = d['user_directory'] / 'historical.csv'

    # Create a new column of datetimes
    # Append to prices
    # Create new csv

    # 'Date' and 'Price' columns are labeled
    # Start and End Dates Match
    # Date format works
    # Longer than 2 weeks
    # Price is just numbers
    # Nonnegative price data
    # Contiguous Data
    # return redirect(url_for('/invalid/<x>'))