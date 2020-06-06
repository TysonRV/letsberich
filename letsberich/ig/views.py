from django.shortcuts import render
from django.views import generic

from letsberich.ig.exceptions import IGServiceError
from letsberich.ig.ig_services import get_ig_api


class IGHome(generic.View):
    ig_api = get_ig_api()

    def get(self, request, *args):
        return render(request, 'ig/ig_home.html', {})

    def post(self, request, *args):
        context = {}
        try:
            watchlists = self.ig_api.get_watchlists()
            context['watchlists'] = watchlists
            # import ipdb; ipdb.set_trace()
        except IGServiceError as api_error:
            context['api_error'] = api_error

        return render(request, 'ig/ig_home.html', context)


class IGPMarkets(generic.View):
    ig_api = get_ig_api()

    def get(self, request, *args):
        return render(request, 'ig/ig-popular_markets.html', {})

    def post(self, request, *args):
        context = {}
        try:
            watchlist_popular_markets = self.ig_api.get_specific_watchlist()
            context['watchlists_popular'] = watchlist_popular_markets

        except IGServiceError as api_error:
            context['api_error'] = api_error

        # import ipdb; ipdb.set_trace()
        return render(request, 'ig/ig-popular_markets.html', context)


class IGMarketNavigation(generic.View):
    ig_api = get_ig_api()

    def get(self, request):
        return render(request, 'ig/market_navigation.html', {})

    def post(self, request):
        context = {}
        try:
            instrument_list = self.ig_api.get_navigation_list()
            context['instrument_list'] = instrument_list

        except IGServiceError as api_error:
            context['api_error'] = api_error

        # import ipdb;ipdb.set_trace()
        return render(request, 'ig/market_navigation.html', context)


class IGNodeNavigation(generic.View):
    ig_api = get_ig_api()

    def get(self, request, **kwargs):

        node_id = kwargs['node_id']
        context = {}
        try:
            node_list = self.ig_api.get_node_list(node_id)
            context['node_list'] = node_list

        except IGServiceError as api_error:
            context['api_error'] = api_error

        return render(request, 'ig/node_list.html', context)


class IGAccountSummary(generic.View):
    ig_api = get_ig_api()

    def get(self, request):
        return render(request, 'ig/summary_required_data.html', {})

    def post(self, request):
        context={}

        try:
            useful_data = self.ig_api.get_account_useful_data()
            context['useful_data'] = useful_data

        except IGServiceError as api_error:
            context['api_error'] = api_error
        # import ipdb; ipdb.set_trace()
        return render(request, 'ig/summary_required_data.html', context)