import os
from HelperFunctions import (
    SetUpEnvironmentVariables,
    SetUpJsonFileForRequest,
    PopulateSlotData,
    SendTextMessage,
    sendWhatsappMessage,
)
import requests
import logging


logging.basicConfig(
    filename="asda.log",
    filemode="a",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)

store = "ASDA"

SetUpEnvironmentVariables(store)
json_data = SetUpJsonFileForRequest(store)

# Make POST request to API, sending required json data
r = requests.post(os.environ["URL"], json=json_data)

slot_data = PopulateSlotData(r)

# Filter for available slots
available_list = [
    f"\n{key} - {value}" for (key, value) in slot_data.items() if value != "UNAVAILABLE"
]

# If any available slots exist, send a text notification
if len(available_list) > 0:
    sendWhatsappMessage(available_list[0])
    logging.info("Message sent inlcuding {}".format(available_list[0]))
else:
    logging.info("No available slots")
