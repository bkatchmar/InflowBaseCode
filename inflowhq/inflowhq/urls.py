from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from inflowco.views import BaseSitemap, IndexView, GoogleDomainVerificationFile, HowItWorksView, AboutUsView, BlogHomeView

sitemaps = {
    'static': BaseSitemap,
}

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^how-it-works$', HowItWorksView.as_view(), name='how_it_works'),
    url(r'^about-inflow$', AboutUsView.as_view(), name='about_us'),
    url(r'^the-watercooler-blog$', BlogHomeView.as_view(), name='blog'),
    url(r'^google255e09f84b6b193b\.html$', GoogleDomainVerificationFile.as_view(), name='google_domain_verification'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^inflow/', include('inflowco.urls')),
    url(r'^account/', include('accounts.urls')),
    url(r'^projects/', include('contractsandprojects.urls')),
    url(r'^stripe/', include('talktostripe.urls')),
    url(r'^inflow/demo/', include('inflowdemo.urls')),
    url(r'^admin/', admin.site.urls)
]

handler404 = 'inflowdemo.views.not_found'
handler500 = 'inflowdemo.views.server_error'