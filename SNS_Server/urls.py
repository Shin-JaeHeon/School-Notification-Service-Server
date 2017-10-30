from django.conf.urls import url
from django.contrib import admin
from server.controller import control, web

urlpatterns = [
    url(r'^admin/', admin.site.urls), url(r'^reg/$', control.register),
    url(r'^login/$', control.login), url(r'^email/$', web.register_check),  url(r'^list/$', web.list_view),  url(r'^signup/$', web.signup),  url(r'^send/$', web.send),
    url(r'^error/$', web.error), url(r'^fcm/$', control.fcm), url(r'^school/$', control.school),
]
handler404 = web.error404
handler500 = web.error500
handler403 = web.error403
handler400 = web.error400
