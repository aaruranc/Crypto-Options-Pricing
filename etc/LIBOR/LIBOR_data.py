import pandas as pd
from math import isnan
import datetime

def option_label(length):

    if length <= 14:
        option_length = str(length) + '-Day-LIBOR'
    else:
        num = length // 30
        option_length = str(num) + '-Month-LIBOR'
    return option_length


def bootstrap_LIBOR(df, num, index):

    if num < 7:
        left_bound = 'Overnight'
        right_bound = '1-Week'
        l = 1
        r = 7
    elif 7 < num < 30:
        left_bound = '1-Week'
        right_bound = '1-Month'
        l = 7
        r = 30
    elif 30 < num < 60:
        left_bound = '1-Month'
        right_bound = '2-Month'
        l = 30
        r = 60
    elif 60 < num < 90:
        left_bound = '2-Month'
        right_bound = '3-Month'
        l = 60
        r = 90
    elif 90 < num < 180:
        left_bound = '3-Month'
        right_bound = '6-Month'
        l = 90
        r = 180
    else:
        left_bound = '6-Month'
        right_bound = '1-Year'
        l = 180
        r = 365

    if df[right_bound][index] == '.' or df[left_bound][index] == '.':
        return ''

    elif isnan(float(df[right_bound][index])) or isnan(float(df[left_bound][index])):
        return ''

    y = float(df[right_bound][index]) - float(df[left_bound][index])
    x = r - l
    m = y / x

    if m == 0:
        return df[right_bound][index]
    else:
        new = ((m * (num - l)) + df[left_bound][index])
        return new


def modify():

    df = pd.read_csv('LIBOR-master.csv')
    print(df)

    n = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 120, 150, 210, 240, 270, 300, 330]
    headers = []
    d = {}
    for num in n:
        title = option_label(num)
        headers.append(title)
        d.update({title: []})

    k = []

    bootstrap_df = pd.DataFrame(columns=headers)
    p = len(df)
    for index in range(p):
        print(index)

        date_info = df['Date'][index].rsplit('/')
        if int(date_info[2]) > 85:
            date_info[2] = int(date_info[2]) + 1900
        else:
            date_info[2] = int(date_info[2]) + 2000

        date = datetime.date(year=date_info[2], month=int(date_info[0]), day=int(date_info[1]))
        print(date)
        k.append(date)

        for num in n:
            d.update({option_label(num): bootstrap_LIBOR(df, num, index)})
        bootstrap_df = bootstrap_df.append(d, ignore_index=True)

    e = {'Datetime': k}
    datetime_df = pd.DataFrame.from_dict(e)

    old_headers = list(df)
    old_headers.remove('Date')
    df = df[old_headers]

    new_df = pd.concat([datetime_df, df, bootstrap_df], axis=1)
    new_df.to_csv('LIBOR.csv', index=False)
    return


if __name__ == '__main__':
    modify()