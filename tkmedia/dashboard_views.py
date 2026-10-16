"""Custom dashboard views for TK Multimedia."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import (
    Service, Project, GalleryItem, ContactMessage, SiteSettings,
)
from .dashboard_forms import SiteSettingsForm


# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────

def _dashboard_context(request, **extra):
    """Common context for all dashboard pages."""
    return {
        "unread_count": ContactMessage.objects.filter(
            status=ContactMessage.STATUS_NEW
        ).count(),
        **extra,
    }


# ─────────────────────────────────────────────────────────
#  OVERVIEW
# ─────────────────────────────────────────────────────────

@login_required
def overview(request):
    stats = {
        "services_total": Service.objects.count(),
        "services_published": Service.objects.filter(is_published=True).count(),
        "projects_total": Project.objects.count(),
        "projects_published": Project.objects.filter(is_published=True).count(),
        "gallery_total": GalleryItem.objects.count(),
        "gallery_published": GalleryItem.objects.filter(is_published=True).count(),
        "messages_total": ContactMessage.objects.count(),
        "messages_new": ContactMessage.objects.filter(
            status=ContactMessage.STATUS_NEW
        ).count(),
    }

    recent_messages = ContactMessage.objects.order_by("-created_at")[:5]
    recent_projects = Project.objects.order_by("-created_at")[:5]

    return render(request, "dashboard/overview.html", _dashboard_context(
        request,
        stats=stats,
        recent_messages=recent_messages,
        recent_projects=recent_projects,
        active="overview",
    ))


# ─────────────────────────────────────────────────────────
#  CONTACT MESSAGES
# ─────────────────────────────────────────────────────────

@login_required
def messages_list(request):
    status_filter = request.GET.get("status", "").strip()
    qs = ContactMessage.objects.order_by("-created_at")

    valid = {"new", "read", "replied", "archived"}
    if status_filter in valid:
        qs = qs.filter(status=status_filter)
    else:
        status_filter = ""

    return render(request, "dashboard/messages.html", _dashboard_context(
        request,
        messages_list=qs,
        active_status=status_filter,
        status_choices=ContactMessage.STATUS_CHOICES,
        active="messages",
    ))


@login_required
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)

    # Auto-mark as read when opened
    if msg.status == ContactMessage.STATUS_NEW:
        msg.status = ContactMessage.STATUS_READ
        msg.save(update_fields=["status"])

    return render(request, "dashboard/message_detail.html", _dashboard_context(
        request,
        msg=msg,
        status_choices=ContactMessage.STATUS_CHOICES,
        active="messages",
    ))


@login_required
@require_POST
def message_set_status(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    new_status = request.POST.get("status", "").strip()
    valid = {"new", "read", "replied", "archived"}
    if new_status in valid:
        msg.status = new_status
        msg.save(update_fields=["status"])
        messages.success(request, f"Message marked as {new_status}.")
    return redirect("dashboard:message_detail", pk=pk)


@login_required
@require_POST
def message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Message deleted.")
    return redirect("dashboard:messages")


# ─────────────────────────────────────────────────────────
#  CONTENT LISTS
# ─────────────────────────────────────────────────────────

@login_required
def services_list(request):
    qs = Service.objects.order_by("display_order", "title")
    return render(request, "dashboard/content_list.html", _dashboard_context(
        request,
        page_title="Services",
        page_subtitle="All services offered",
        items=qs,
        item_type="service",
        add_url="/admin/tkmedia/service/add/",
        active="services",
    ))


@login_required
def projects_list(request):
    qs = Project.objects.order_by("-created_at")
    return render(request, "dashboard/content_list.html", _dashboard_context(
        request,
        page_title="Projects",
        page_subtitle="Portfolio projects",
        items=qs,
        item_type="project",
        add_url="/admin/tkmedia/project/add/",
        active="projects",
    ))


@login_required
def gallery_list(request):
    qs = GalleryItem.objects.order_by("display_order", "-created_at")
    return render(request, "dashboard/content_list.html", _dashboard_context(
        request,
        page_title="Gallery",
        page_subtitle="Public gallery items",
        items=qs,
        item_type="gallery",
        add_url="/admin/tkmedia/galleryitem/add/",
        active="gallery",
    ))


# ─────────────────────────────────────────────────────────
#  SITE SETTINGS
# ─────────────────────────────────────────────────────────

@login_required
def settings_edit(request):
    obj = SiteSettings.load()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings saved.")
            return redirect("dashboard:settings")
    else:
        form = SiteSettingsForm(instance=obj)

    return render(request, "dashboard/settings.html", _dashboard_context(
        request,
        form=form,
        active="settings",
    ))