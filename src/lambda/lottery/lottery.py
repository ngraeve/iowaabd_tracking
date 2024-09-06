import json
import boto3
import os

import requests
from bs4 import BeautifulSoup

ssm_client = boto3.client('ssm')


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


def get_old_data():
    parameter = ssm_client.get_parameter(Name=os.environ['lottery_parameter_name'])
    print(parameter)
    return parameter['Parameter']['Value']


def write_new_data(new_data):
    print('writing to file')

def lambda_handler(event, context):
    old = get_old_data()
    print(old)
    new = get_data()

    if new != old:
        write_new_data(new)
        print('found a difference')
