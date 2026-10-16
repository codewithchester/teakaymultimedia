# """
# URL configuration for teakaymultimedia project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """

# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path('', include('tkmedia.urls'))
# ]




from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Simple health endpoint — useful for deployment monitoring."""
    return JsonResponse({"status": "ok", "brand": settings.BRAND_NAME})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("tkmedia.dashboard_urls", namespace="dashboard")),
    path("dashboard/vault/", include("vault.urls")),
    path("health/", health_check, name="health_check"),
    path("", include("tkmedia.urls")),
]

# Serve public media in development only.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)