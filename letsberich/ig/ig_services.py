import json
import requests

from django.conf import settings
from django.core.cache import cache
from requests import Response

from letsberich.ig.exceptions import IGServiceError


class IGService(object):

    def __init__(self):
        self.account_id = settings.IG['ACCOUNT_ID_SPREAD_BET']
        self.username = settings.IG['USERNAME']
        self.password = settings.IG['PASSWORD']
        self.api_key = settings.IG['API_KEY']
        self.api_base_url = settings.IG['HOST']

        self.headers = self.get_headers()

        self.oauth_token = None

    def _get_endpoint(self, endpoint: str) -> str:
        return self.api_base_url + settings.IG['URLS'][endpoint]

    def _make_request(self, url, payload=None, method='GET', version=None) -> Response:
        if version:
            self.headers['VERSION'] = version

        if method == 'POST':
            response = requests.post(url, json=payload, headers=self.headers)
        else:
            response = requests.get(url, headers=self.headers)

        return response

    def get_headers(self) -> dict:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=UTF-8',
            'VERSION': '3',
            'X-IG-API-KEY': self.api_key,
            'IG-ACCOUNT-ID': self.account_id
        }
        return headers

    def get_token(self) -> None:
        oauth_token = cache.get('access_token')
        renew_cache = False

        if not oauth_token:
            renew_cache = True
            if self.oauth_token:
                oauth_token = self.refresh_token()
            else:
                url = self._get_endpoint('GET_TOKEN')
                payload = {
                    'identifier': self.username,
                    'password': self.password
                }
                response = self._make_request(url, payload, method='POST')

                if response.status_code < 300:
                    response_dict = json.loads(response.content.decode('utf-8'))

                    oauth_token = response_dict['oauthToken']
                else:
                    raise IGServiceError

        access_token = oauth_token['access_token']
        expires_in = oauth_token['expires_in']

        if renew_cache:
            cache.set('access_token', oauth_token, int(expires_in))

        self.headers['Authorization'] = 'Bearer ' + access_token
        self.oauth_token = oauth_token

    def refresh_token(self) -> dict:
        url = self._get_endpoint('REFRESH_TOKEN')
        payload = {
            'refresh_token': self.oauth_token['refresh_token'],
        }

        response = self._make_request(url, payload, method='POST', version='1')
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))

            access_token = response_dict['access_token']
            self.headers['Authorization'] = 'Bearer ' + access_token

            return response_dict
        else:
            raise IGServiceError

    def get_watchlists(self):
        self.get_token()

        url = self._get_endpoint('WATCHLISTS')

        response = self._make_request(url, version='1')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['watchlists']
        else:
            raise IGServiceError

    def get_specific_watchlist(self) -> dict:
        self.get_token()

        url = self._get_endpoint('SPECIFIC_WATCHLIST').format('Popular Markets')
        response = self._make_request(url, version='1')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['markets']
        else:
            raise IGServiceError

    def get_navigation_list(self) -> dict:
        self.get_token()

        url = self._get_endpoint('INSTRUMENT_LIST')
        response = self._make_request(url, version='1')
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['nodes']
        else:
            raise IGServiceError

    def get_node_list(self, node_id) -> dict:
        self.get_token()

        url = self._get_endpoint('NODE_NAVIGATION').format(node_id)
        response = self._make_request(url, version='1')
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['nodes']
        else:
            raise IGServiceError

    def get_prices(self):
        # TODO

        self.get_token()

        url = self._get_endpoint('PRICES').format('KA.D.VOD.CASH.IP')

        response = self._make_request(url, version='3')

    def get_account_useful_data(self):
        self.get_token()
        url = self._get_endpoint('ACCOUNT_USEFUL_DATA')
        response = self._make_request(url, version='2')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['positions']
        else:
            raise IGServiceError

    def create_position(self, payload: dict) -> Response:
        self.get_token()
        url = self._get_endpoint('OPEN_POSITION')

        cleaned_payload = {
            'currency_code': payload['currency_code'],
            'deal_reference': payload['deal_reference'],
            'direction': payload['direction'],
            'epic': payload['epic'],
            'expiry': payload['expiry'].strftime('%Y-%m-%d'),
            'force_open': payload['force_open'],
            'guaranteed_stop': payload['guaranteed_stop'],
            'order_type': payload['order_type'],
            'size': payload['size'],
            'stop_level': payload['stop_level'],
        }

        response = self._make_request(
            url,
            payload=cleaned_payload,
            method='POST',
            version='2'
        )
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['dealReference']
        else:
            raise IGServiceError(
                "Error creating a position: {}".format(response.content)
            )


def get_ig_api() -> IGService:
    return IGService()
