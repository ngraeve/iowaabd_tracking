import json

import requests
from bs4 import BeautifulSoup


def get_data():
    r = requests.get('https://shop.iowaabd.com/snapshot/lottery').text
    soup = BeautifulSoup(r, 'html.parser')
    table = soup.find('table', id='lottery-table')
    rows = table.find_all('tr')
    data = {}

    for tr in rows:
        td = tr.find_all('td')
        if len(td) == 0:
            continue
        data[td[1].text.strip()] = td[2].text.strip()

    return data


def write_new_data(new_data):
    print('writing to file')
    with open('sample_data.json', 'w') as f:
        json.dump(new_data, f)


with open('./sample_data.json') as json_data:
    old = json.load(json_data)

new = get_data()

if new != old:
    write_new_data(new)
