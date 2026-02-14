import requests
import base64
from datetime import datetime
import os

class MpesaService:
    def __init__(self):
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.shortcode = os.getenv('MPESA_SHORTCODE')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL')
        env = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
        self.base_url = 'https://sandbox.safaricom.co.ke' if env == 'sandbox' else 'https://api.safaricom.co.ke'

    def get_token(self):
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        auth = base64.b64encode(f'{self.consumer_key}:{self.consumer_secret}'.encode()).decode()
        headers = {'Authorization': f'Basic {auth}'}
        try:
            response = requests.get(url, headers=headers)
            return response.json().get('access_token')
        except:
            return None

    def stk_push(self, phone, amount, order_id):
        token = self.get_token()
        if not token:
            return {'success': False, 'message': 'Failed to get token'}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f'{self.shortcode}{self.passkey}{timestamp}'.encode()).decode()
        
        url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone,
            'PartyB': self.shortcode,
            'PhoneNumber': phone,
            'CallBackURL': self.callback_url,
            'AccountReference': f'Order{order_id}',
            'TransactionDesc': f'Payment for Order {order_id}'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except:
            return {'success': False, 'message': 'STK Push failed'}
