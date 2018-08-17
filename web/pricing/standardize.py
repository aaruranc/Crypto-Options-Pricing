from pathlib import Path
import pandas as pd
import datetime


def verify_dates(df, start, end):
    return


def validate(user_parameters):

    start = user_parameters['start']
    end = user_parameters['end']
    trading_days = user_parameters['trading_days']
    source = Path(user_parameters['source'])

    error = []
    df = pd.read_csv(source)
    n = len(df)
    headers = list(df)

    if 'Date' not in headers:
        error.append('Date not labeled correctly in csv')
    if 'Price' not in headers:
        error.append('Price not labeled correctly in csv')
    if len(headers) > 2:
        error.append('Too Many Columns')
    if df['Date'][0] != start:
        error.append('Start Date Incorrect')
    if df['Date'][n-1] != end:
        error.append('End Date Incorrect')
    # if n < 14:
    #     error.append('csv must be longer than 2 weeks')



    for index, series in df.iterrows():
        if df['Price'][index] < 0:
            if 'Negative Prices not Allowed' not in error:
                error.append('Negative Prices not Allowed')




    return

if __name__ == '__main__':

    loc = Path('data/AAPL')
    d = {'asset': 'AAPL', 'start': '01/01/0000', 'end': '12/31/10', 'trading_days': 'weekdays',
         'source': 'data/1534366837/BTC.csv'}

    # Verify Start, End and Contiguity of Data
    file = d['user_directory'] / 'historical.csv'

    # Create a new column of datetimes
    # Append to prices
    # Create new csv
    # Longer than 2 weeks
    # Price is just numbers
    # Nonnegative price data
    # Contiguous Data
    # return redirect(url_for('/invalid/<x>'))

