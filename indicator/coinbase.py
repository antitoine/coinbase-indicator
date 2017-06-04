from __future__ import print_function
import sys
import json
import requests
import time

from .backend import Backend

COINBASE_API_URL = 'https://api.coinbase.com/'
COINBASE_URL = 'https://www.coinbase.com/'
COINBASE_API_VERSION = 'v2'
COINBASE_API_VERSION_DATE = '2017-06-03'


class Coinbase(Backend):

    def __init__(self):
        self.real_currency = 'EUR'

    def get_available_real_currencies(self):
        return ['EUR', 'USD']

    def set_real_currency(self, real_currency):
        self.real_currency = real_currency

    def get_real_currency(self):
        return self.real_currency

    def get_available_crypto_currencies(self):
        return ['BTC', 'ETH', 'LTC']

    def get_spot_price(self, crypto_currency):
        data = self.__get('prices/' + crypto_currency + '-' + self.real_currency + '/spot')
        if 'amount' in data:
            return data['amount']
        else:
            return -1

    def get_store_url(self):
        return COINBASE_URL

    @staticmethod
    def __get(uri):
        response = None
        while response is None:
            try:
                response = requests.get(
                    COINBASE_API_URL + COINBASE_API_VERSION + '/' + uri,
                    headers={
                        'content-type': 'application/json',
                        'CB-VERSION': COINBASE_API_VERSION_DATE,
                    },
                )
            except requests.exceptions.RequestException as e:
                print('Error - Unable to make the request to the Coinbase API - ' + str(e), file=sys.stderr)
                time.sleep(10)

        json_data = json.loads(response.text)
        if 'warnings' in json_data:
            for warning in json_data['warnings']:
                print('Warning - '
                      + (warning['message'] if 'message' in warning else '')
                      + (' - ' + warning['id'] if 'id' in warning else '')
                      + (' - ' + warning['url'] if 'url' in warning else ''), file=sys.stderr)
        if 'errors' in json_data:
            for error in json_data['errors']:
                print('Error - '
                      + (error['message'] if 'message' in error else '')
                      + (' - ' + error['id'] if 'id' in error else '')
                      + (' - ' + error['url'] if 'url' in error else ''), file=sys.stderr)
        if 'data' in json_data:
            return json_data['data']
        else:
            return json_data