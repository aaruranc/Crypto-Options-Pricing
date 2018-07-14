import pandas as pd
from date import str_adjust
from collections import OrderedDict


def index_vals(step_3, start):
    cols = [0, 1, 2, 3, 4]
    metrics = pd.read_csv("CCI30/CCI30.csv", usecols=cols)
    index_start = str_adjust(metrics['Date'][0], len(metrics['Date'][0]))

    match = 0
    if start[6:] < index_start[6:]:
        for series, index in step_3.iterrows():
            if step_3['Date'][series] == index_start:
                match = series
                route = 'A'
                break

    if start[6:] == index_start[6:]:
        if start[0:2] > start[0:2]:
            for series,index in metrics.iterrows():
                if metrics['Date'][series] == start:
                    match = series
                    route = 'B'
                    break



    header_tags = ['CCI30 Open', 'CCI30 High', 'CCI30 Low', 'CCI30 Close']
    headers = OrderedDict.fromkeys(header_tags, [])
    df = pd.DataFrame.from_dict(headers)
    dict = {}

    count = 0

    for series, index in step_3.iterrows():
        if route == 'A':
            if series < match:
                for val in header_tags:
                    dict.update({val: 'NaN'})
            else:
                for val in header_tags:
                    dict.update({val: metrics[val][count]})
                count = count + 1

            df = df.append(dict, ignore_index=True)

        if route == 'B':
            for val in header_tags:
                dict.update({val: metrics[val][match]})
            match = match + 1
        df = df.append(dict, ignore_index=True)




    step_4 = pd.concat([step_3, df], axis=1)
    return step_4
