import json

import os
import logging

import requests
from bs4 import BeautifulSoup

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
ssm_client = boto3.client('ssm')


def get_ssm_parameter_value(parameter_name):
    logger.info(f'Retrieving {parameter_name} from parameter store')

    try:
        response = ssm_client.get_parameter(Name=parameter_name)['Parameter']['Value']
        logger.info(f'Response is {response}')
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            logger.error(f'Parameter {parameter_name} not found')
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            logger.error(f'Access denied to parameter {parameter_name}')
        else:
            logger.error(f'An error occurred: {e}')
        return None


def get_live_data(url):
    logger.info(f'Sending request to {url}')
    r = requests.get(url).text
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


def write_new_data(parameter_name, new_data):
    logger.info(f'Updating value of {parameter_name} parameter')
    try:
        response = ssm_client.put_parameter(
            Name=parameter_name,
            Value=new_data,
            Overwrite=True
        )
        logger.info("Parameter successfully updated:", response)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Error updating parameter: {error_code} - {error_message}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


def lambda_handler(event, context):
    old_dict = get_ssm_parameter_value(os.environ['lottery_current_list_parameter_name'])
    new_dict = get_live_data(get_ssm_parameter_value(os.environ['lottery_url_parameter_name']))

    if new_dict != old_dict:
        logger.info('Website has updated')
        write_new_data(os.environ['lottery_current_list_parameter_name'], new_dict)

