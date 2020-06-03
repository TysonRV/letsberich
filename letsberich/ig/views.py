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
        except IGServiceError as api_error:
            context['api_error'] = api_error

        return render(request, 'ig/ig_home.html', context)
