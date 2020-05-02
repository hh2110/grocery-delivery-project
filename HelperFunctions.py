import os
import configparser
from datetime import datetime, timedelta
import logging
from twilio.rest import Client


config = configparser.ConfigParser()
config.read("shops.conf")

logging.basicConfig(
    filename="asda.log",
    filemode="a",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)


def SetUpEnvironmentVariables(groceryStore):
    """
    sets up environment with information based on the grocery-store
    param: groceryStore str
    return: none
    """
    parameterList = [
        "POSTCODE",
        "LATITUDE",
        "LONGITUDE",
        "ACT_ID",
        "TWILIO_ACT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_NUMBER",
        "TWILIO_WHATSAPP_NUMBER",
        "MY_NUMBER",
    ]

    if os.environ["COMPUTERNAME"] == "UK-L-0318":
        for parameter in parameterList:
            os.environ[parameter] = config[groceryStore][parameter]

    os.environ["URL"] = config[groceryStore]["URL"]
    os.environ["START_DATE"] = datetime.today().date().strftime("%Y-%m-%dT%H:%M:%S")
    os.environ["END_DATE"] = (datetime.today().date() + timedelta(days=14)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


def SetUpJsonFileForRequest(groceryStore):
    """
    sets up json string for the request
    param: groceryStore str
    return: none
    """
    json_data = {
        "requestorigin": "gi",
        "data": {
            "service_info": {"fulfillment_type": "DELIVERY", "enable_express": "false"},
            "start_date": os.environ["START_DATE"],
            "end_date": os.environ["END_DATE"],
            "reserved_slot_id": "",
            "service_address": {
                "postcode": os.environ["POSTCODE"],
                "latitude": os.environ["LATITUDE"],
                "longitude": os.environ["LONGITUDE"],
            },
            "customer_info": {"account_id": os.environ["ACT_ID"]},
            "order_info": {
                "order_id": "20983571638",
                "restricted_item_types": [],
                "volume": 0,
                "weight": 0,
                "sub_total_amount": 0,
                "line_item_count": 0,
                "total_quantity": 0,
            },
        },
    }

    return json_data


def PopulateSlotData(requestString):
    """
    parse the string returned from the url request
    param: requestString str
    return: dictionary containing info about slots
    """
    # Initialise empty dictionary for data
    slot_data = {}

    # Loop through json response and record slot status for each time slot
    if requestString.json()["data"]:
        for slot_day in requestString.json()["data"]["slot_days"]:
            slot_date = slot_day["slot_date"]
            for slot in slot_day["slots"]:
                slot_time = slot["slot_info"]["start_time"]
                slot_time = datetime.strptime(slot_time, "%Y-%m-%dT%H:%M:%SZ")
                slot_status = slot["slot_info"]["status"]
                slot_data[slot_time.strftime("%H:%M:%S %d-%m-%Y")] = slot_status
    else:
        logging.info("No slot data to look into.")

    return slot_data


def SendTextMessage(messageTxt):
    """
    sending message with twilio
    """
    account_sid = os.environ["TWILIO_ACT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    client.messages.create(
        body=messageTxt, from_=os.environ["TWILIO_NUMBER"], to=os.environ["MY_NUMBER"]
    )


def sendWhatsappMessage(messageTxt):
    """
    sending whatsapp message with twilio
    """
    account_sid = os.environ["TWILIO_ACT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    client.messages.create(
        body=messageTxt,
        from_=os.environ["TWILIO_WHATSAPP_NUMBER"],
        to="whatsapp:" + os.environ["MY_NUMBER"],
    )
