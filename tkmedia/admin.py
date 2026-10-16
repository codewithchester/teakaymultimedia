# from django.contrib import admin

# # Register your models here.
"""Admin registration for TK MULTIMEDIA content."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Service, Project, ProjectImage


# ─────────────────────────────────────────────────────────
#  SERVICE
# ─────────────────────────────────────────────────────────

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title", "display_order", "starting_price",
        "is_published", "updated_at",
    )
    list_editable = ("display_order", "is_published")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "cover_preview")

    fieldsets = (
        ("Identity", {
            "fields": ("title", "slug", "icon")
        }),
        ("Content", {
            "fields": ("short_description", "description")
        }),
        ("Media", {
            "fields": ("cover_image", "cover_preview")
        }),
        ("Pricing (optional)", {
            "fields": ("starting_price", "price_note"),
            "classes": ("collapse",),
        }),
        ("Publishing", {
            "fields": ("is_published", "published_at", "display_order")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:160px;border-radius:6px;" />',
                obj.cover_image.url,
            )
        return "—"
    cover_preview.short_description = "Cover preview"


# ─────────────────────────────────────────────────────────
#  PROJECT IMAGES (inline)
# ─────────────────────────────────────────────────────────

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "caption", "display_order")
    ordering = ("display_order",)


# ─────────────────────────────────────────────────────────
#  PROJECT
# ─────────────────────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "is_featured",
        "is_published", "completed_on", "display_order",
    )
    list_editable = ("is_featured", "is_published", "display_order")
    list_filter = ("category", "is_featured", "is_published", "completed_on")
    search_fields = ("title", "summary", "description", "technologies")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "cover_preview")
    date_hierarchy = "created_at"
    inlines = [ProjectImageInline]

    fieldsets = (
        ("Identity", {
            "fields": ("title", "slug", "category")
        }),
        ("Content", {
            "fields": ("summary", "description", "technologies")
        }),
        ("Media", {
            "fields": ("cover_image", "cover_preview")
        }),
        ("Links", {
            "fields": ("external_url", "source_url"),
            "classes": ("collapse",),
        }),
        ("Publishing", {
            "fields": ("is_featured", "is_published", "published_at",
                       "completed_on", "display_order")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:160px;border-radius:6px;" />',
                obj.cover_image.url,
            )
        return "—"
    cover_preview.short_description = "Cover preview"


# ─────────────────────────────────────────────────────────
#  ADMIN BRANDING
# ─────────────────────────────────────────────────────────

admin.site.site_header = "TK MULTIMEDIA — Administration"
admin.site.site_title = "TK MULTIMEDIA Admin"
admin.site.index_title = "Content & Site Management"






# ─────────────────────────────────────────────────────────
#  STAGE 4 — NEW ADMIN REGISTRATIONS
# ─────────────────────────────────────────────────────────

from .models import ContactMessage, GalleryItem, Skill, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message",
                       "ip_address", "user_agent", "created_at", "updated_at")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    actions = ["mark_read", "mark_replied", "mark_archived"]

    fieldsets = (
        ("Sender", {
            "fields": ("name", "email", "phone", "ip_address", "user_agent")
        }),
        ("Message", {
            "fields": ("subject", "message")
        }),
        ("Status", {
            "fields": ("status",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.action(description="Mark selected as Read")
    def mark_read(self, request, queryset):
        queryset.update(status=ContactMessage.STATUS_READ)

    @admin.action(description="Mark selected as Replied")
    def mark_replied(self, request, queryset):
        queryset.update(status=ContactMessage.STATUS_REPLIED)

    @admin.action(description="Archive selected")
    def mark_archived(self, request, queryset):
        queryset.update(status=ContactMessage.STATUS_ARCHIVED)


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "display_order", "created_at")
    list_editable = ("is_published", "display_order")
    list_filter = ("category", "is_published")
    search_fields = ("title", "alt_text", "caption")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "display_order")
    list_editable = ("display_order",)
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Singleton — the 'add' button is disabled. Only edit.
    """
    fieldsets = (
        ("Brand", {
            "fields": ("brand_name", "tagline", "footer_text")
        }),
        ("Homepage", {
            "fields": ("homepage_headline", "homepage_intro",
                       "homepage_audio", "homepage_audio_transcript")
        }),
        ("About", {
            "fields": ("about_story", "about_philosophy"),
            "classes": ("collapse",),
        }),
        ("Contact", {
            "fields": ("contact_email", "contact_whatsapp")
        }),
        ("Legal", {
            "fields": ("privacy_policy", "terms_of_use"),
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        # Only one row allowed
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False