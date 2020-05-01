import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from twilio.rest import Client
import configparser
import logging

logging.basicConfig(filename='asda.log', filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)

config = configparser.ConfigParser()
config.read('shops.conf')

if os.environ['COMPUTERNAME'] == 'UK-L-0318':
    os.environ['POSTCODE'] = config['ASDA']['POSTCODE']
    os.environ['LATITUDE'] = config['ASDA']['LATITUDE']
    os.environ['LONGITUDE'] = config['ASDA']['LONGITUDE']
    os.environ['ACT_ID'] = config['ASDA']['ACT_ID']
    os.environ['TWILIO_ACT_SID'] = config['ASDA']['TWILIO_ACT_SID']
    os.environ['TWILIO_AUTH_TOKEN'] = config['ASDA']['TWILIO_AUTH_TOKEN']
    os.environ['TWILIO_NUMBER'] = config['ASDA']['TWILIO_NUMBER']
    os.environ['MY_NUMBER'] = config['ASDA']['MY_NUMBER']

url = 'https://groceries.asda.com/api/v3/slot/view'

start_date = datetime.today().date().strftime('%Y-%m-%dT%H:%M:%S')
end_date = (datetime.today().date() + timedelta(days=14)
            ).strftime('%Y-%m-%dT%H:%M:%S')

json_data = {"requestorigin": "gi",
             "data": {"service_info": {"fulfillment_type": "DELIVERY",
                                       "enable_express": 'false'},
                      "start_date": start_date,
                      "end_date": end_date,
                      "reserved_slot_id": "",
                      "service_address": {"postcode": os.environ['POSTCODE'],
                                          "latitude": os.environ['LATITUDE'],
                                          "longitude": os.environ['LONGITUDE']},
                      "customer_info": {"account_id": os.environ['ACT_ID']},
                      "order_info": {"order_id": "20983571638",
                                     "restricted_item_types": [],
                                     "volume": 0, "weight": 0,
                                     "sub_total_amount": 0,
                                     "line_item_count": 0,
                                     "total_quantity": 0}}}

# Make POST request to API, sending required json data
r = requests.post(url, json=json_data)

# Initialise empty dictionary for data
slot_data = {}

# Loop through json response and record slot status for each time slot
for slot_day in r.json()['data']['slot_days']:

    slot_date = slot_day['slot_date']

    for slot in slot_day['slots']:

        slot_time = slot['slot_info']['start_time']
        slot_time = datetime.strptime(slot_time, '%Y-%m-%dT%H:%M:%SZ')

        slot_status = slot['slot_info']['status']

        slot_data[slot_time.strftime('%H:%M:%S %d-%m-%Y')] = slot_status

# Filter for available slots
available_list = [
    f'\n{key} - {value}' for (key, value) in slot_data.items() if value != 'UNAVAILABLE']

# If any available slots exist, send a text notification
if len(available_list) > 0:

    account_sid = os.environ['TWILIO_ACT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message_txt = f'\nDelivery Slot/s Found: \n{" ".join(available_list)}'

    message = client.messages \
                    .create(
                        body=message_txt,
                        from_=os.environ['TWILIO_NUMBER'],
                        to=os.environ['MY_NUMBER']
                    )
    logging.info('Message sent inlcuding {}'.format(available_list))
else:
    logging.info('No available slots')
