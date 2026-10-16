from django.urls import path
from . import views

app_name = "vault"

urlpatterns = [
    path("", views.home, name="home"),

    # Files
    path("files/", views.file_list, name="file_list"),
    path("files/upload/", views.upload, name="upload"),
    path("files/<int:pk>/", views.file_detail, name="file_detail"),
    path("files/<int:pk>/download/", views.download, name="download"),
    path("files/<int:pk>/preview/", views.preview, name="preview"),
    path("files/<int:pk>/edit/", views.file_edit, name="file_edit"),
    path("files/<int:pk>/delete/", views.file_delete, name="file_delete"),
    path("files/<int:pk>/restore/", views.file_restore, name="file_restore"),
    path("files/<int:pk>/purge/", views.file_purge, name="file_purge"),

    # Trash
    path("trash/", views.trash, name="trash"),

    # Folders
    path("folders/new/", views.folder_create, name="folder_create"),
    path("folders/<int:pk>/", views.folder_detail, name="folder_detail"),
    path("folders/<int:pk>/delete/", views.folder_delete, name="folder_delete"),

    # Audit log
    path("audit/", views.audit_log, name="audit_log"),
]
