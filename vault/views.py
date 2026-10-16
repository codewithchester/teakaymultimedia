# from django.shortcuts import render

# # Create your views here.
"""Views for the private vault."""
import mimetypes
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from tkmedia.models import ContactMessage

from .forms import VaultUploadForm, FolderCreateForm, FileEditForm
from .models import PrivateFile, PrivateFolder, VaultAuditLog


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

# Only these image types are safe to render inline in a browser.
SAFE_INLINE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def _unread_count():
    return ContactMessage.objects.filter(status=ContactMessage.STATUS_NEW).count()


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _log(request, action, file_obj=None, folder=None, file_name=""):
    VaultAuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        file_name=file_name or (file_obj.original_name if file_obj else ""),
        file_id=file_obj.pk if file_obj else None,
        folder_id=folder.pk if folder else None,
        ip_address=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
    )


def _dashboard_context(request, **extra):
    """Common sidebar context for vault templates."""
    return {
        "unread_count": _unread_count(),
        **extra,
    }


def _owns(user, obj):
    """True if user owns obj OR is staff."""
    return obj.owner_id == user.pk or user.is_staff


# ══════════════════════════════════════════════════════════
#  HOME / OVERVIEW
# ══════════════════════════════════════════════════════════

@login_required
def home(request):
    """Vault overview — stats, recent uploads, storage usage."""
    files_qs = PrivateFile.objects.filter(owner=request.user, is_deleted=False)
    folders_qs = PrivateFolder.objects.filter(owner=request.user)

    total_size = files_qs.aggregate(total=Sum("size"))["total"] or 0

    recent_files = files_qs[:8]
    recent_folders = folders_qs[:6]

    return render(request, "dashboard/vault/home.html", _dashboard_context(
        request,
        total_files=files_qs.count(),
        total_folders=folders_qs.count(),
        total_size=total_size,
        trash_count=PrivateFile.objects.filter(owner=request.user, is_deleted=True).count(),
        recent_files=recent_files,
        recent_folders=recent_folders,
        active="vault",
    ))


# ══════════════════════════════════════════════════════════
#  FILE LIST / FOLDER DETAIL
# ══════════════════════════════════════════════════════════

@login_required
def file_list(request):
    """All files (root view, with search + filter)."""
    query = request.GET.get("q", "").strip()
    folder_id = request.GET.get("folder", "").strip()

    qs = PrivateFile.objects.filter(owner=request.user, is_deleted=False)

    if query:
        from django.db.models import Q
        qs = qs.filter(
            Q(original_name__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
        )

    if folder_id == "none":
        qs = qs.filter(folder__isnull=True)
    elif folder_id:
        qs = qs.filter(folder_id=folder_id)

    folders = PrivateFolder.objects.filter(owner=request.user)

    return render(request, "dashboard/vault/list.html", _dashboard_context(
        request,
        files=qs,
        folders=folders,
        current_folder=None,
        query=query,
        active="vault",
    ))


@login_required
def folder_detail(request, pk):
    """Files inside a specific folder."""
    folder = get_object_or_404(PrivateFolder, pk=pk)
    if not _owns(request.user, folder):
        raise Http404

    query = request.GET.get("q", "").strip()
    qs = PrivateFile.objects.filter(owner=request.user, folder=folder, is_deleted=False)
    if query:
        from django.db.models import Q
        qs = qs.filter(
            Q(original_name__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
        )

    return render(request, "dashboard/vault/list.html", _dashboard_context(
        request,
        files=qs,
        folders=PrivateFolder.objects.filter(owner=request.user),
        current_folder=folder,
        query=query,
        active="vault",
    ))


# ══════════════════════════════════════════════════════════
#  UPLOAD
# ══════════════════════════════════════════════════════════

@login_required
def upload(request):
    """Upload a file. Accepts GET (form) and POST (upload)."""
    initial = {}
    folder_id = request.GET.get("folder", "").strip()
    if folder_id:
        initial["folder"] = folder_id

    if request.method == "POST":
        form = VaultUploadForm(request.POST, request.FILES, owner=request.user)
        if form.is_valid():
            uploaded = form.cleaned_data["file"]

            obj = PrivateFile(
                original_name=uploaded.name[:300],
                file=uploaded,
                owner=request.user,
                folder=form.cleaned_data.get("folder"),
                description=form.cleaned_data.get("description", ""),
                tags=form.cleaned_data.get("tags", ""),
            )
            # Detect mime type from filename (best-effort)
            guessed, _ = mimetypes.guess_type(uploaded.name)
            obj.mime_type = guessed or uploaded.content_type or "application/octet-stream"
            obj.save()

            _log(request, "upload", file_obj=obj, folder=obj.folder)

            messages.success(request, f"Uploaded “{obj.original_name}”.")
            return redirect("vault:file_detail", pk=obj.pk)
        else:
            messages.error(request, "Upload failed. Please fix the errors below.")
    else:
        form = VaultUploadForm(owner=request.user, initial=initial)

    return render(request, "dashboard/vault/upload.html", _dashboard_context(
        request,
        form=form,
        active="vault",
    ))


# ══════════════════════════════════════════════════════════
#  FILE DETAIL
# ══════════════════════════════════════════════════════════

@login_required
def file_detail(request, pk):
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    return render(request, "dashboard/vault/detail.html", _dashboard_context(
        request,
        file=file_obj,
        active="vault",
    ))


# ══════════════════════════════════════════════════════════
#  DOWNLOAD (protected)
# ══════════════════════════════════════════════════════════

@login_required
def download(request, pk):
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    if not file_obj.file:
        raise Http404

    # Defense in depth: verify the resolved path stays inside PRIVATE_MEDIA_ROOT
    try:
        storage_path = Path(file_obj.file.path).resolve()
        base_path = Path(settings.PRIVATE_MEDIA_ROOT).resolve()
        if not str(storage_path).startswith(str(base_path)):
            raise Http404
    except (ValueError, NotImplementedError):
        # Storage backend doesn't support .path — trust FileResponse
        pass

    if not file_obj.file.storage.exists(file_obj.file.name):
        messages.error(request, "File is missing from storage.")
        return redirect("vault:file_detail", pk=file_obj.pk)

    _log(request, "download", file_obj=file_obj, folder=file_obj.folder)

    file_handle = file_obj.file.storage.open(file_obj.file.name, "rb")

    content_type = file_obj.mime_type or "application/octet-stream"

    response = FileResponse(file_handle, content_type=content_type)
    response["Content-Length"] = file_obj.size
    response["Content-Disposition"] = (
        f'attachment; filename="{quote(file_obj.original_name)}"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


# ══════════════════════════════════════════════════════════
#  PREVIEW (inline — safe images only)
# ══════════════════════════════════════════════════════════

@login_required
def preview(request, pk):
    """Serve safe image files inline (never SVG, never HTML)."""
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    if file_obj.extension not in SAFE_INLINE_EXTENSIONS:
        raise Http404

    if not file_obj.file or not file_obj.file.storage.exists(file_obj.file.name):
        raise Http404

    _log(request, "download", file_obj=file_obj, folder=file_obj.folder)

    file_handle = file_obj.file.storage.open(file_obj.file.name, "rb")
    content_type = file_obj.mime_type or mimetypes.guess_type(file_obj.original_name)[0] or "image/png"

    response = FileResponse(file_handle, content_type=content_type)
    response["Content-Security-Policy"] = "default-src 'none'; img-src 'self';"
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, max-age=1800"
    return response


# ══════════════════════════════════════════════════════════
#  EDIT
# ══════════════════════════════════════════════════════════

@login_required
def file_edit(request, pk):
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    if request.method == "POST":
        form = FileEditForm(request.POST, owner=request.user)
        if form.is_valid():
            file_obj.original_name = form.cleaned_data["original_name"][:300]
            file_obj.description = form.cleaned_data.get("description", "")
            file_obj.tags = form.cleaned_data.get("tags", "")
            file_obj.folder = form.cleaned_data.get("folder")
            file_obj.save()

            _log(request, "rename", file_obj=file_obj, folder=file_obj.folder)

            messages.success(request, "File updated.")
            return redirect("vault:file_detail", pk=file_obj.pk)
    else:
        form = FileEditForm(owner=request.user, initial={
            "original_name": file_obj.original_name,
            "description": file_obj.description,
            "tags": file_obj.tags,
            "folder": file_obj.folder_id,
        })

    return render(request, "dashboard/vault/edit.html", _dashboard_context(
        request,
        form=form,
        file=file_obj,
        active="vault",
    ))


# ══════════════════════════════════════════════════════════
#  DELETE / RESTORE / PURGE
# ══════════════════════════════════════════════════════════

@login_required
@require_POST
def file_delete(request, pk):
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    file_obj.soft_delete()
    _log(request, "delete", file_obj=file_obj, folder=file_obj.folder)
    messages.success(request, f"“{file_obj.original_name}” moved to trash.")
    return redirect("vault:file_list")


@login_required
@require_POST
def file_restore(request, pk):
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    file_obj.restore()
    _log(request, "restore", file_obj=file_obj, folder=file_obj.folder)
    messages.success(request, f"“{file_obj.original_name}” restored.")
    return redirect("vault:trash")


@login_required
@require_POST
def file_purge(request, pk):
    """Permanently delete a file. No undo."""
    file_obj = get_object_or_404(PrivateFile, pk=pk)
    if not _owns(request.user, file_obj):
        raise Http404

    name = file_obj.original_name
    _log(request, "purge", file_obj=file_obj, folder=file_obj.folder)
    file_obj.delete()  # also removes bytes from disk

    messages.success(request, f"“{name}” permanently deleted.")
    return redirect("vault:trash")


# ══════════════════════════════════════════════════════════
#  TRASH
# ══════════════════════════════════════════════════════════

@login_required
def trash(request):
    qs = PrivateFile.objects.filter(owner=request.user, is_deleted=True)
    return render(request, "dashboard/vault/trash.html", _dashboard_context(
        request,
        files=qs,
        active="vault",
    ))


# ══════════════════════════════════════════════════════════
#  FOLDERS
# ══════════════════════════════════════════════════════════

@login_required
def folder_create(request):
    if request.method == "POST":
        form = FolderCreateForm(request.POST, owner=request.user)
        if form.is_valid():
            folder = PrivateFolder.objects.create(
                name=form.cleaned_data["name"][:200],
                parent=form.cleaned_data.get("parent"),
                owner=request.user,
            )
            _log(request, "folder_create", folder=folder)
            messages.success(request, f"Folder “{folder.name}” created.")
            return redirect("vault:folder_detail", pk=folder.pk)
    else:
        initial = {}
        parent_id = request.GET.get("parent", "").strip()
        if parent_id:
            initial["parent"] = parent_id
        form = FolderCreateForm(owner=request.user, initial=initial)

    return render(request, "dashboard/vault/folder_form.html", _dashboard_context(
        request,
        form=form,
        active="vault",
    ))


@login_required
@require_POST
def folder_delete(request, pk):
    folder = get_object_or_404(PrivateFolder, pk=pk)
    if not _owns(request.user, folder):
        raise Http404

    name = folder.name
    _log(request, "folder_delete", folder=folder, file_name=name)

    # Move files out of the folder (don't delete them)
    PrivateFile.objects.filter(folder=folder).update(folder=None)
    folder.delete()

    messages.success(request, f"Folder “{name}” deleted. Files were kept.")
    return redirect("vault:home")


# ══════════════════════════════════════════════════════════
#  AUDIT LOG
# ══════════════════════════════════════════════════════════

@login_required
def audit_log(request):
    """Browse all vault operations recorded in the audit log."""
    # Staff see everything, regular users see only their own
    if request.user.is_staff:
        qs = VaultAuditLog.objects.select_related("user")
    else:
        qs = VaultAuditLog.objects.filter(user=request.user).select_related("user")

    # Filters
    action_filter = request.GET.get("action", "").strip()
    valid_actions = {key for key, _ in VaultAuditLog.ACTION_CHOICES}
    if action_filter in valid_actions:
        qs = qs.filter(action=action_filter)
    else:
        action_filter = ""

    qs = qs[:200]  # Cap at 200 rows for performance

    return render(request, "dashboard/vault/audit.html", _dashboard_context(
        request,
        logs=qs,
        action_choices=VaultAuditLog.ACTION_CHOICES,
        active_action=action_filter,
        active="vault",
    ))