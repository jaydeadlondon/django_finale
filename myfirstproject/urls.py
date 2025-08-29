from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from shopapp.sitemaps import ShopSitemap
from django.contrib.sitemaps.views import sitemap

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

sitemaps = {
    'shop': ShopSitemap,
}

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('shop/', include('shopapp.urls')),
    path('api/', include('myapiapp.urls')),
    path('accounts/', include('myauth.urls')),
    path("blog/", include("blogapp.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))