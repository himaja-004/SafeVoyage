import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_sos_alert_fast2sms(numbers, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        'authorization': os.getenv('FAST2SMS_API_KEY'),
        'Content-Type': 'application/json'
    }

    payload = {
        'sender_id': 'FSTSMS',
        'message': message,
        'language': 'english',
        'route': 'q',
        'numbers': ",".join(numbers),
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Fast2SMS Response:", response.json())
