from django.conf.urls import url
from django.contrib import admin
from server.controller import control

urlpatterns = [
    url(r'^admin/', admin.site.urls), url(r'^reg/$', control.register),
    url(r'^login/', control.login), url(r'^email/', control.register_check),  url(r'^setting/', control.setting)
]
