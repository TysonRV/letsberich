from django.conf.urls import url

from letsberich.ig import views

urlpatterns = [
    url(r'^$', views.IGHome.as_view(), {}, name='ig-home'),
]
