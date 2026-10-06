import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/NajuVerutti/flasky/.env')

response = requests.post(
    os.getenv('API_URL'),
    auth=('api', os.getenv('API_KEY')),
    data={
        'from': os.getenv('API_FROM'),
        'to': [
            os.getenv('FLASKY_ADMIN'),
            os.getenv('PERSONAL_EMAIL')
        ],
        'subject': 'Flasky Mailgun Test',
        'text': 'This is a test email sent through Mailgun.'
    }
)

print('Status:', response.status_code)
print('Response:', response.text)
