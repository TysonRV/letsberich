from django.conf.urls import url
from django.urls import path

from letsberich.ig import views

urlpatterns = [
    url(r'^$', views.IGHome.as_view(), {}, name='ig-home'),
    url(r'^popular_markets/$', views.IGPMarkets.as_view(), {}, name='ig-popular_markets'),
    url(r'^market_navigation/$', views.IGMarketNavigation.as_view(), {},
        name='market_navigation'),
    path('node_navigation/<node_id>/', views.IGNodeNavigation.as_view(), name='node_navigation'),
    path('account_summary/', views.IGAccountSummary.as_view(), name='account_summary')
]
