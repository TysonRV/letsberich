from django.urls import path

from letsberich.ig import views

urlpatterns = [
    path('', views.IGHome.as_view(), {}, name='ig-home'),
    path(
        'popular_markets/',
        views.IGPMarkets.as_view(),
        {},
        name='ig-popular-markets'
    ),
    path(
        'market_navigation/',
        views.IGMarketNavigation.as_view(),
        {},
        name='market-navigation'
    ),
    path(
        'node_navigation/<node_id>/',
        views.IGNodeNavigation.as_view(),
        name='node-navigation'
    ),
    path('account_summary/', views.IGAccountSummary.as_view(), name='account-summary'),
    path('open_position/', views.IGOpenPosition.as_view(), name='open-position')
]
