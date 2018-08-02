from pathlib import Path

if __name__ == '__main___':
    # Initialize User Directory
    user_directory = Path('data') / test_u_i['Name']
    file_name = 'historical' + '.csv'
    user_csv = user_directory / file_name

    # Initialize Option Lengths
    option_lengths = test_a_c['Option Lengths']


    # Initialize Strike Prices & Trading Strategies
    strikes = test_a_c['Strikes']
    strategies = test_a_c['Strategies']

    print('start debugging')

    # # Compute Put and Call Prices across Strike Prices
    # # Needs Debugged
    BS_prices(user_directory, option_lengths, strikes)

    print('Black-Scholes Pricing Finished')
    return
