from pathlib import Path
import pandas as pd
import json
import datetime, time


def price_JSON(current_file):

    df = pd.read_csv(current_file)

    b = []
    for index, series in df.iterrows():
        a = []
        a.append(int(df['Timestamp'][index]))
        a.append(df['Price'][index])
        b.append(a)

    data = json.dumps(b)
    # y = json.JSONEncoder().encode(b)
    return data

#
# def probability_density_JSON(df, method):
#
#     payoff = method + '-P'
#     payoff_df = df(columns=['Date', payoff]).copy()
#     sorted_df = payoff_df.sort_values(by=[payoff])
#     sorted_df.reset_index(drop=True)
#
#     size = len(sorted_df)
#     first_quartile = size // 4
#     third_quartile = (size // 4) * 3
#     IQR = third_quartile - first_quartile
#
#     # Freedman-Diaconis Rule
#     bin_width = (1 / np.cbrt(size)) * 2 * IQR
#
#     count = 0
#     bin_count = 1
#     b = []
#     for index, series in sorted_df.iterrows():
#         if sorted_df[payoff][index] > (bin_count * bin_width):
#             b.append({(bin_count * bin_width): count})
#             count = 0
#             bin_count = bin_count + 1
#             continue
#         count = count + 1
#
#     num_bins = len(b)
#     d = {'bins': num_bins, 'width': bin_width, 'data': b}
#     return d


def LIBOR_label(rf_rates):

    if rf_rates == '1-Day':
        return '1-Day-LIBOR'
    elif rf_rates == '1-Week':
        return '1-Week-LIBOR'
    elif rf_rates == '1-Month':
        return '1-Month-LIBOR'
    elif rf_rates == '2-Month':
        return '2-Month-LIBOR'
    elif rf_rates == '3-Month':
        return '3-Month-LIBOR'
    elif rf_rates == '6-Month':
        return '6-Month-LIBOR'
    elif rf_rates == '1-Year':
        return '1-Year-LIBOR'
    else:
        return 'Synthetic LIBOR'

def option_label(length):
    
    if length <= 14:
        option_length = str(length) + '-Day'
    elif 14 < length < 365:
        num = length // 30
        option_length = str(num) + '-Month'
    else:
        option_length = '1-Year'
    return option_length


def UNIX_timestamp(val):
    x = int(time.mktime(val.timetuple()))*1000
    return x


def query_JSON(query):

    trading_strategy = query['trading_strategy']
    length = int(query['option_length'])
    strike = int(query['strike'])
    current_directory = Path(query['current_directory'])
    source = Path(query['source'])
    trading_days = query['trading_days']

    method = str(strike) + '-' + trading_strategy
    option_length = option_label(length)
    rf_rates = option_length + '-LIBOR'
    rf_header = LIBOR_label(option_length)
    returns = method + '-ROI'
    vol = option_length + '-VM'

    current_file = option_length + '.csv'
    file_loc = current_directory / current_file
    df = pd.read_csv(file_loc)

    k = []
    for index, series in df.iterrows():
        if index <= length:
            continue

        j = [int(df['Timestamp'][index]), float("{0:.2f}".format(df[vol][index]))]
        k.append(j)

    y = json.JSONEncoder().encode(k)
    return y


    # pdf = probability_density_JSON(df, method)
    #
    # end = datetime.datetime(year=2018, month=7, day=5)
    # end_check = UNIX_timestamp(end)
    #
    # headers = [option_length + '-' + 'VM', 'VIX']
    #
    # c = []
    # for title in headers:
    #     b = []
    #     for index, series in df.iterrows():
    #         a = []
    #         print(df['Datetime'][index])
    #         if index <= length + 1:
    #             continue
    #         elif df['Timestamp'][index] == end_check:
    #             break
    #
    #         a.append(int(df['Timestamp'][index]))
    #         a.append(df[title][index])
    #         b.append(a)
    #
    #     d = {'name': title, 'data': b}
    #     c.append(d)
    #
    #     k = {'Price': df['Price'][index], 'Vol-Mean': df['Vol-Mean'][index], 'Vol-No-Mean': df['Vol-No-Mean'][index],
    #          'Strategy-Cost': df[method][index], rf_header: df[rf_rates][index], 'ROI': df[returns][index],
    #          'Probability-Density': pdf}
    #
    #     k = {'Date': df['Datetime'][index], 'Price': df['Price'][index]}
    #     p = {df['Date'][index]: k}
    #     a.append(k)
    #
    # df_length = len(a)
    # d = {'length': df_length, 'type': 'Query', 'data': a}

    # print(b)
    # y = json.JSONEncoder().encode(c)
    # print(y)
    # print(type(y))
    # return y


if __name__ == '__main__':

    seriesOptions[i] = {
        name: name,
        data: data
    };
    test_query = {'trading_strategy': 'Calls', 'option_length': '3', 'strike': '90',
                  'current_directory': 'data/1534716161', 'source': 'data/1534716161/AAPL.csv'}
    print('export_data main executed')
