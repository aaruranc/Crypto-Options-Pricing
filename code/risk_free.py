from math import isnan
from collections import OrderedDict
import pandas as pd
from normalize_date import str_adjust


def parse_rates():
    libor = 'LIBOR.csv'
    df = pd.read_csv(libor)

    headers = ['Overnight', '1-Week', '1-Month', '2-Month', '3-Month', '6-Month']

    for series, index in df.iterrows():
        date = df.loc[series, 'Date']
        new_date = str_adjust(date, len(str(date)))
        df.loc[series, 'Date'] = new_date

    for title in headers:
        print(title)
        temp = ''
        for series, index in df.iterrows():
            if df.at[series, title] == '':
                continue
            elif df.at[series, title] != '.':
                temp = df.at[series, title]
            elif df.at[series, title] == '.':
                df.at[series, title] = temp

    print(df)
    return df


def interest_rates(step_2, start):

    cols = [0, 1, 2, 3, 4, 5]
    rates = pd.read_csv("risk_free_rates.csv", usecols=cols)
    index_start = str_adjust(rates['Date'][0], len(rates['Date'][0]))

    # match = 0
    # route = 0
    # if start[6:] < index_start[6:]:
    #     for series, index in step_2.iterrows():
    #         if step_2['Date'][series] == index_start:
    #             match = series
    #             route = 'A'
    #             break
    #
    # if start[6:] == index_start[6:]:
    #     if start[0:2] > index_start[0:2]:
    #         for series, index in rates.iterrows():
    #             if str_adjust(rates['Date'][series], len(rates['Date'][series])) == start:
    #                 match = series
    #                 route = 'B'
    #                 break


    header_tags = ['1 Month Treasury Bill', '3 Month Treasury Bill', '6 Month Treasury Bill', '1 Year Treasury Bill',
                   '2 Year Treasury Bill']
    headers = OrderedDict.fromkeys(header_tags, [])
    df = pd.DataFrame.from_dict(headers)
    d = {}

    weekday = 0
    numskips = 0
    for series, index in step_2.iterrows():
        skipped = 2 * numskips
        if weekday == 5:
            count = series - skipped - 1
            weekday = weekday + 1
        elif weekday == 6:
            count = series - skipped - 2
            weekday = 0
            numskips = numskips + 1
        else:
            count = series - skipped
            weekday = weekday + 1
        for val in header_tags:
            d.update({val: rates[val][count]})
        df = df.append(d, ignore_index=True)
    step_3 = pd.concat([step_2, df], axis=1)
    return step_3