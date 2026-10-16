from django.urls import path
from . import dashboard_views as dv

app_name = "dashboard"

urlpatterns = [
    path("", dv.overview, name="overview"),

    # Messages
    path("messages/", dv.messages_list, name="messages"),
    path("messages/<int:pk>/", dv.message_detail, name="message_detail"),
    path("messages/<int:pk>/status/", dv.message_set_status, name="message_set_status"),
    path("messages/<int:pk>/delete/", dv.message_delete, name="message_delete"),

    # Content
    path("services/", dv.services_list, name="services"),
    path("projects/", dv.projects_list, name="projects"),
    path("gallery/", dv.gallery_list, name="gallery"),

    # Settings
    path("settings/", dv.settings_edit, name="settings"),
]