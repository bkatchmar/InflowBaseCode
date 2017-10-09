from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^inflow/', include('inflowco.urls')),
    url(r'^inflow/account/', include('accounts.urls')),
    url(r'^inflow/projects/', include('contractsandprojects.urls')),
    url(r'^inflow/stripe/', include('talktostripe.urls')),
    url(r'^admin/', admin.site.urls),
]