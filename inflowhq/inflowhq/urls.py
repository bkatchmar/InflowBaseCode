from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from inflowco.views import BaseSitemap, LoginView, GoogleDomainVerificationFile

sitemaps = {
    'static': BaseSitemap,
}

urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^google255e09f84b6b193b\.html$', GoogleDomainVerificationFile.as_view(), name='google_domain_verification'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^inflow/', include('inflowco.urls')),
    url(r'^inflow/account/', include('accounts.urls')),
    url(r'^inflow/projects/', include('contractsandprojects.urls')),
    url(r'^inflow/stripe/', include('talktostripe.urls')),
    url(r'^inflow/demo/', include('inflowdemo.urls')),
    url(r'^admin/', admin.site.urls)
]

handler404 = 'inflowdemo.views.not_found'
handler500 = 'inflowdemo.views.server_error'