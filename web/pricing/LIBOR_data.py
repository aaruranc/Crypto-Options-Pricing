import pandas as pd
from math import isnan

def option_label(length):

    if length <= 14:
        option_length = str(length) + '-Day-LIBOR'
    else:
        num = length // 30
        option_length = str(num) + '-Month-LIBOR'
    return option_length


def bootstrap_LIBOR(df, num, index):

    if num < 7:
        left_bound = '1-Day-LIBOR'
        right_bound = '7-Day-LIBOR'
        l = 1
        r = 7
    elif 7 < num < 30:
        left_bound = '7-Day-LIBOR'
        right_bound = '1-Month-LIBOR'
        l = 7
        r = 30
    elif 30 < num < 60:
        left_bound = '1-Month-LIBOR'
        right_bound = '2-Month-LIBOR'
        l = 30
        r = 60
    elif 60 < num < 90:
        left_bound = '2-Month-LIBOR'
        right_bound = '3-Month-LIBOR'
        l = 60
        r = 90
    elif 90 < num < 180:
        left_bound = '3-Month-LIBOR'
        right_bound = '6-Month-LIBOR'
        l = 90
        r = 180
    else:
        left_bound = '6-Month-LIBOR'
        right_bound = '1-Year-LIBOR'
        l = 180
        r = 365

    if df[right_bound][index] == '.' or df[left_bound][index] == '.':
        return ''

    if isnan(float(df[right_bound][index])) or isnan(float(df[left_bound][index])):
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

    df = pd.read_csv('LIBOR.csv')
    n = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 90, 120, 150, 210, 240, 270, 300, 330]
    headers = []
    d = {}
    for num in n:
        title = option_label(num)
        headers.append(title)
        d.update({title: []})

    bootstrap_df = pd.DataFrame(columns=headers)

    l = len(df)
    q = l // 4
    h = l // 2
    t = q * 3

    for index, series in df.iterrows():
        print(index)
        if index == q:
            print('Quarter Done')
        if index == h:
            print('Halfway Done')
        if index == t:
            print('Three-Quarters Done')

        count = 0
        for num in n:
            d.update({option_label(num): bootstrap_LIBOR(df, num, index)})
            count = count + 1
        bootstrap_df = bootstrap_df.append(d, ignore_index=True)
    df = pd.concat([df, bootstrap_df], axis=0)
    df.to_csv('LIBOR.csv')
    return


if __name__ == '__main__':
    modify()