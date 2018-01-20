from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from inflowco.views import BaseSitemap

sitemaps = {
    'static': BaseSitemap,
}

urlpatterns = [
    url(r'^inflow/', include('inflowco.urls')),
    url(r'^inflow/account/', include('accounts.urls')),
    url(r'^inflow/projects/', include('contractsandprojects.urls')),
    url(r'^inflow/stripe/', include('talktostripe.urls')),
    url(r'^inflow/demo/', include('inflowdemo.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]