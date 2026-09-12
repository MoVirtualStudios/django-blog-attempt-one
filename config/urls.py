from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from blog import views as blog_views
from blog.sitemaps import PostSitemap, StaticViewSitemap


sitemaps = {
    "posts": PostSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls'),),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": sitemaps,
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path(
        "robots.txt",
        blog_views.robots_txt,
        name="robots_txt",
    ),
    path('', include('blog.urls'),),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

handler404 = "blog.views.custom_404"
handler500 = "blog.views.custom_500"