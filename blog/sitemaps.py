from django.contrib import sitemaps
from django.urls import reverse

from .models import Post

class PostSitemap(sitemaps.Sitemap):

    changefreq = "weekly"
    priority = 0.8

    def items(self):

        return (
            Post.objects
            .published()
            .order_by("-published_at")
        )

    def lastmod(self, obj):

        return obj.updated_at


class StaticViewSitemap(sitemaps.Sitemap):

    changefreq = "monthly"
    priority = 0.5

    def items(self):

        return [
            "blog:post_list",
            "blog:about",
            "blog:contact",
        ]

    def location(self, item):

        return reverse(item)