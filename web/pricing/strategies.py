import pandas as pd


def missing_strikes(query, strategy):

    strike = int(query['strike'])

    if strategy == 'Calls' or strategy == 'Puts':
        return []
    elif strategy == 'Straddles' or strategy == 'Straps' or strategy == 'Strips' or strategy == 'Calendar-Spreads':
        return []
    elif strategy == 'Bear-Spreads':
        return [strike - 5]
    elif strategy == 'Bull-Spreads':
        return [strike + 5]
    elif strategy == 'Butterfly-Spreads':
        return [strike - 2, strike + 2]
    elif strategy == 'Strangles':
        return [strike - 3, strike + 3]
    else:
        return []


def strategy_payoff(query, df, index, strategy, cost):

    if str(cost) == '':
        return 0

    length = int(query['option_length'])
    new_index = index + length
    df_length = len(df)

    if new_index >= df_length:
        return ''

    strike = int(query['strike'])
    ratio = strike / 100

    strike_price = df['Price'][index] * ratio
    expiration_price = df['Price'][new_index]

    if strategy == 'Straddles' or strategy == 'Straps' or strategy == 'Strips':

        dec_payoff = strike_price - expiration_price
        inc_payoff = expiration_price - strike_price

        if strategy == 'Straps':
            inc_payoff = 2 * inc_payoff
        elif strategy == 'Strips':
            dec_payoff = 2 * dec_payoff

        if strike_price > expiration_price:
            return dec_payoff - cost
        elif expiration_price > strike_price:
            return inc_payoff - cost
        else:
            return 0

    elif strategy == 'Bear-Spreads' or strategy == 'Bull-Spreads':
        if strategy == 'Bear-Spreads':
            if expiration_price < (strike - 5):
                return 5 - cost
            elif (strike - 5) <= expiration_price <= strike:
                return strike - expiration_price - cost
            elif strike < expiration_price:
                return -cost
            else:
                return ''
        else:
            if expiration_price < strike:
                return -cost
            elif strike <= expiration_price <= (strike + 5):
                return expiration_price - strike - cost
            elif (strike + 5) < expiration_price:
                return 5 - cost
            else:
                return ''

    elif strategy == 'Butterfly-Spreads':
        low_call = (ratio - .02) * df['Price'][index]
        high_call = (ratio + .02) * df['Price'][index]

        if expiration_price <= low_call or expiration_price >= high_call:
            return -cost
        elif low_call < expiration_price < strike:
            return expiration_price - low_call - cost
        elif strike <= expiration_price <= high_call:
            return high_call - expiration_price - cost
        else:
            return ''

    elif strategy == 'Strangles':
        put = (ratio - .03) * df['Price'][index]
        call = (ratio + .03) * df['Price'][index]
        print('Strike Price')
        print(strike_price)
        print('Expiration Price')
        print(expiration_price)
        print('Put')
        print(put)
        print('Call')
        print(call)
        print('Cost')
        print(cost)

        if expiration_price <= put:
            return put - expiration_price - cost
        elif put < expiration_price < call:
            return -cost
        elif call <= expiration_price:
            return expiration_price - call - cost
        else:
            return ''

    else:
        return ''


def compute(query, query_file, strategy):
    strike = int(query['strike'])
    call = str(strike) + '-Calls'
    put = str(strike) + '-Puts'

    df = pd.read_csv(query_file)

    m = []
    p = []
    r = []

    for index in range(len(df)):

        if str(df[call][index]) == '' or str(df[put][index]) == '':
            cost = ''
            profit = ''
            returns = ''
        else:
            cost = ''
            if strategy == 'Straddles':
                cost = df[call][index] + df[put][index]
            elif strategy == 'Straps':
                cost = 2 * df[call][index] + df[put][index]
            elif strategy == 'Strips':
                cost = df[call][index] + (2 * df[put][index])
            elif strategy == 'Bear-Spreads':
                short_strike = strike - 5
                short_put = str(short_strike) + '-Puts'
                cost = df[put][index] - df[short_put][index]
            elif strategy == 'Bull-Spreads':
                short_strike = strike + 5
                short_call = str(short_strike) + '-Calls'
                cost = df[put][index] - df[short_call][index]
            elif strategy == 'Butterfly-Spreads':
                low_call_strike = strike - 2
                high_call_strike = strike + 2
                low_call = str(low_call_strike) + '-Calls'
                high_call = str(high_call_strike) + '-Calls'
                cost = df[low_call][index] + df[high_call] - (2 * df[put][index])
            elif strategy == 'Strangles':
                put_strike = strike - 3
                call_strike = strike + 3
                long_call = str(call_strike) + '-Calls'
                long_put = str(put_strike) + '-Puts'
                cost = df[long_call][index] + df[long_put][index]

            profit = strategy_payoff(query, df, index, strategy, cost)

            if str(profit) == '' or str(cost) == '':
                returns = ''
            else:
                returns = 100 * profit / cost

        m.append(cost)
        p.append(profit)
        r.append(returns)

    strike = str(strike)
    method = strike + '-' + strategy
    payoff = method + '-P'
    ROI = method + '-ROI'
    d = {method: m, payoff: p, ROI: r}

    new_df = pd.DataFrame.from_dict(d)
    df = pd.concat([df, new_df], axis=1)
    df.to_csv(query_file, index=False)
    return
