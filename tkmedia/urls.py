from django.urls import path
from . import views

app_name = "tkmedia"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("portfolio/<slug:slug>/", views.project_detail, name="project_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]




# from django.urls import path 
# from . import views

# urlpatterns = [
#     path('', views.home, name="home"),
# ]



# from django.urls import path
# from . import views

# app_name = "tkmedia"

# urlpatterns = [
#     path("", views.home, name="home"),
# ]