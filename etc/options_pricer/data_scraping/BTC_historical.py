import requests
import datetime
import operator
import csv


def gather_data():
    url = "https://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-17&end=2018-07-01"
    response = requests.get(url)
    data_price_pairs = response.json()["bpi"]
    return data_price_pairs


def convert_keys_to_timestamps(data):
    new_dict = {}
    for key in list(data.keys()):
        datetime_key = datetime.datetime.strptime(key, "%Y-%m-%d")
        new_dict[datetime_key] = data[key]

    return new_dict


def parse_into_csv(data_price_pairs):
    with open("historical_bitcoin_data.csv", 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["Date", "Price ($)"])
        for pair in data_price_pairs:
            csv_out.writerow(pair)


def gather_prices():
    data = gather_data()
    parsed_data = convert_keys_to_timestamps(data)
    sorted_data = sorted(parsed_data.items(), key=operator.itemgetter(0))
    parse_into_csv(sorted_data)
