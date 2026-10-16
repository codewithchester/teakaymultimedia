from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse

from tkmedia.sitemaps import StaticViewSitemap, ServiceSitemap, ProjectSitemap


def health_check(request):
    """Simple health endpoint — useful for deployment monitoring."""
    return JsonResponse({"status": "ok", "brand": settings.BRAND_NAME})


def robots_txt(request):
    """
    robots.txt — tells crawlers what to index.
    Note: robots.txt is NOT access control. Sensitive paths
    are protected by authentication, not by this file.
    """
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /dashboard/vault/",
        "Disallow: /health/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# Sitemap registry
sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "projects": ProjectSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("tkmedia.dashboard_urls", namespace="dashboard")),
    path("dashboard/vault/", include("vault.urls")),
    path("health/", health_check, name="health_check"),

    # SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),

    # Public site
    path("", include("tkmedia.urls")),
]

# Serve public media in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)