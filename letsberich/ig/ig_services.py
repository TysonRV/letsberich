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

    def get_instrument_characteristics(self, epic: str):
        self.get_token()
        url = self._get_endpoint('GET_INSTRUMENT_CHARACTERISTICS').format(epic)
        response = self._make_request(url, version='3')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict
        else:
            raise IGServiceError

    def get_account_useful_data(self):
        self.get_token()
        url = self._get_endpoint('ACCOUNT_USEFUL_DATA')
        response = self._make_request(url, version='2')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['positions']
        else:
            raise IGServiceError

    def create_position(self, payload: dict) -> dict:
        self.get_token()
        url = self._get_endpoint('CREATE_POSITION')

        cleaned_payload = {
            'currencyCode': payload['currency_code'],
            'dealReference': payload['deal_reference'],
            'direction': payload['direction'],
            'epic': payload['epic'],
            'expiry': payload['expiry'],
            'forceOpen': payload['force_open'],
            'guaranteedStop': payload['guaranteed_stop'],
            'orderType': payload['order_type'],
            'size': payload['size'],
            'stopLevel': payload['stop_level'],
        }
        response = self._make_request(
            url,
            payload=cleaned_payload,
            method='POST',
            version='2'
        )

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict
        else:
            raise IGServiceError(
                "Error creating a position: {}".format(response.content)
            )

    def confirm_position(self, deal_ref: dict) -> dict:
        self.get_token()

        url = self._get_endpoint('CONFIRM_POSITION').format(deal_ref['dealReference'])
        response = self._make_request(url, version='1')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict
        raise IGServiceError("Error creating a position: {}".format(response.content))

    def open_position(self, deal_id: dict) -> dict:
        self.get_token()

        url = self._get_endpoint('OPEN_POSITION').format(deal_id['dealId'])
        response = self._make_request(url, version='2')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict
        raise IGServiceError("Error creating a position: {}".format(response.content))

    def open_position_wrapper(self, payload: dict):
        self.get_token()

        deal_ref = self.create_position(payload)
        deal_id = self.confirm_position(deal_ref)
        open_position_data = self.open_position(deal_id)
        return open_position_data

    def get_instrument_list(self) -> dict:
        self.get_token()
        url = self._get_endpoint('SPECIFIC_WATCHLIST').format('12047692') #weekend_watch is 12047692; pm_watchlist id is 11899563. ftse_watchlist is 11899563
        response = self._make_request(url, version='1')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['markets']
        raise IGServiceError("Error getting watchlist: {}".format(response.content))

    def get_past_price(self, instrument: dict, data_points: int):
        self.get_token()
        url = self._get_endpoint('GET_HISTORICAL_PRICES').format(instrument['epic'], 'MINUTE', data_points)
        response = self._make_request(url, version='2')

        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['prices']

        raise IGServiceError("Error getting past price: {}".format(response.content))

    def close_position_wrapper(self): #TODO
        return 1

def get_ig_api() -> IGService:
    return IGService()
