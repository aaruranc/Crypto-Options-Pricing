import math
from collections import  OrderedDict
import pandas as pd


def parse_rates(rates):
    parsed_rates = []
    last_rate = None
    for rate in rates:
        if math.isnan(rate):
            continue
        else:
            last_rate = rate
        parsed_rates.append(last_rate)
    return parsed_rates


def interest_rates(step_2, start):
    cols = [0, 1, 2, 3, 4, 5]
    rates = pd.read_csv("risk_free_rates.csv", usecols=cols)

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