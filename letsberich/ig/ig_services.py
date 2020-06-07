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
        # import ipdb;ipdb.set_trace()
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['nodes']
            # import ipdb; ipdb.set_trace()
        else:
            raise IGServiceError

    @staticmethod
    def hello():
        return 1

    def get_node_list(self, node_id) -> dict:
        self.get_token()

        url = self._get_endpoint('NODE_NAVIGATION').format(node_id)
        response = self._make_request(url, version='1')
        # import ipdb;ipdb.set_trace()
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['nodes']
            # import ipdb; ipdb.set_trace()
        else:
            raise IGServiceError

    def get_prices(self):
        # TODO

        self.get_token()

        url = self._get_endpoint('PRICES').format('KA.D.VOD.CASH.IP')

        response = self._make_request(url, version='3')
        # import ipdb; ipdb.set_trace()

    def _get_endpoint(self, endpoint: str) -> str:
        return self.api_base_url + settings.IG['URLS'][endpoint]

    def _make_request(self, url, payload=None, method='GET', version=None) -> Response:
        if version:
            self.headers['VERSION'] = version

        if method == 'POST':
            response = requests.post(url, json=payload, headers=self.headers)
        else:
            # import ipdb; ipdb.set_trace()
            response = requests.get(url, headers=self.headers)

        return response

    def get_account_useful_data(self):
        self.get_token()
        url = self._get_endpoint('ACCOUNT_USEFUL_DATA')
        response = self._make_request(url, version='2')

        # import ipdb; ipdb.set_trace()
        if response.status_code < 300:
            response_dict = json.loads(response.content.decode('utf-8'))
            return response_dict['positions']
        else:
            return IGServiceError

    def create_position(self, otc_position: dict) -> Response:
        self.get_token()
        url = self._get_endpoint('OPEN_POSITION')

        response = self._make_request(url, payload=otc_position, method='POST', version='2')
        import ipdb; ipdb.set_trace()
        return response

def get_ig_api() -> IGService:
    return IGService()
