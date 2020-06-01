from django.shortcuts import render
from django.views import generic

from letsberich.ig.ig_services import get_ig_api


class IGHome(generic.View):
    ig_api = get_ig_api()

    def get(self, request, *args):
        return render(request, 'ig/ig_home.html', {})

    def post(self, request, *args):
        watchlists = self.ig_api.get_watchlists()

        context = {
            'watchlists': watchlists,
        }

        return render(request, 'ig/ig_home.html', context)
