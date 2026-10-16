"""Public views for TK MULTIMEDIA."""
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from .forms import ContactForm
from .models import (
    Service, Project, GalleryItem, Skill, SiteSettings,
)


# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def is_rate_limited(request, key: str, limit: int, window: int) -> bool:
    """
    Simple cache-based rate limiter.
    limit = max requests per window seconds.
    """
    ip = get_client_ip(request) or "unknown"
    cache_key = f"rl:{key}:{ip}"
    count = cache.get(cache_key, 0)
    if count >= limit:
        return True
    cache.set(cache_key, count + 1, window)
    return False


# ─────────────────────────────────────────────────────────
#  PUBLIC PAGES
# ─────────────────────────────────────────────────────────

def home(request):
    """Homepage — hero, services preview, featured projects, audio, contact CTA."""
    settings_obj = SiteSettings.load()

    featured_projects = (
        Project.objects
        .filter(is_published=True, is_featured=True)
        .prefetch_related("images")[:3]
    )
    services = Service.objects.filter(is_published=True)[:4]

    return render(request, "tkmedia/home.html", {
        "featured_projects": featured_projects,
        "services": services,
        "settings_obj": settings_obj,
    })


def about(request):
    """About page — shows skills from DB."""
    settings_obj = SiteSettings.load()
    technical_skills = Skill.objects.filter(category="technical")
    creative_skills = Skill.objects.filter(category="creative")
    tools = Skill.objects.filter(category="tool")

    return render(request, "tkmedia/about.html", {
        "settings_obj": settings_obj,
        "technical_skills": technical_skills,
        "creative_skills": creative_skills,
        "tools": tools,
    })


def services(request):
    services_qs = Service.objects.filter(is_published=True)
    return render(request, "tkmedia/services.html", {"services": services_qs})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_published=True)
    other_services = Service.objects.filter(is_published=True).exclude(pk=service.pk)[:4]
    return render(request, "tkmedia/service_detail.html", {
        "service": service,
        "other_services": other_services,
    })


def portfolio(request):
    category = request.GET.get("category", "").strip().lower()
    projects = Project.objects.filter(is_published=True).prefetch_related("images")

    valid_categories = {key for key, _ in Project.CATEGORY_CHOICES}
    if category and category in valid_categories:
        projects = projects.filter(category=category)
    else:
        category = ""

    return render(request, "tkmedia/portfolio.html", {
        "projects": projects,
        "active_category": category,
        "categories": Project.CATEGORY_CHOICES,
    })


def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related("images"),
        slug=slug,
        is_published=True,
    )
    related = (
        Project.objects
        .filter(is_published=True, category=project.category)
        .exclude(pk=project.pk)
        .prefetch_related("images")[:3]
    )
    return render(request, "tkmedia/project_detail.html", {
        "project": project,
        "related_projects": related,
    })


def gallery(request):
    category = request.GET.get("category", "").strip().lower()
    items = GalleryItem.objects.filter(is_published=True)

    valid_categories = {key for key, _ in GalleryItem.CATEGORY_CHOICES}
    if category and category in valid_categories:
        items = items.filter(category=category)
    else:
        category = ""

    return render(request, "tkmedia/gallery.html", {
        "items": items,
        "active_category": category,
        "categories": GalleryItem.CATEGORY_CHOICES,
    })


# ─────────────────────────────────────────────────────────
#  CONTACT
# ─────────────────────────────────────────────────────────

@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact page with server-side validation, honeypot, and rate limiting."""
    settings_obj = SiteSettings.load()

    if request.method == "POST":
        # Rate limit: 5 submissions per 10 minutes per IP
        if is_rate_limited(request, "contact", limit=5, window=600):
            messages.error(
                request,
                "Too many submissions. Please wait a few minutes and try again.",
            )
            return render(request, "tkmedia/contact.html", {
                "form": ContactForm(request.POST),
                "settings_obj": settings_obj,
            }, status=429)

        form = ContactForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.ip_address = get_client_ip(request)
            obj.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
            obj.save()

            messages.success(
                request,
                "Thank you — your message has been received. I'll get back to you soon.",
            )
            return redirect("tkmedia:contact")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, "tkmedia/contact.html", {
        "form": form,
        "settings_obj": settings_obj,
    })


# ─────────────────────────────────────────────────────────
#  LEGAL
# ─────────────────────────────────────────────────────────

def privacy(request):
    settings_obj = SiteSettings.load()
    return render(request, "tkmedia/privacy.html", {"settings_obj": settings_obj})


def terms(request):
    settings_obj = SiteSettings.load()
    return render(request, "tkmedia/terms.html", {"settings_obj": settings_obj})


# ─────────────────────────────────────────────────────────
#  ROBOTS (placeholder — full SEO in Stage 10)
# ─────────────────────────────────────────────────────────

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")