"""Sitemaps for SEO — tells Google which public URLs to index."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Service, Project


class StaticViewSitemap(Sitemap):
    """Public static pages: home, about, services, portfolio, gallery, contact, privacy, terms."""
    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return [
            "tkmedia:home",
            "tkmedia:about",
            "tkmedia:services",
            "tkmedia:portfolio",
            "tkmedia:gallery",
            "tkmedia:contact",
            "tkmedia:privacy",
            "tkmedia:terms",
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """All published services."""
    priority = 0.7
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Service.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    """All published projects."""
    priority = 0.7
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at