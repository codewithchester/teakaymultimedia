# from django.db import models

# # Create your models here.


"""
Content models for TK MULTIMEDIA.

Public content only. Private files (vault) live in a separate app
introduced in Stage 8 — keeping public and private data physically
and logically separated.
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator


# ─────────────────────────────────────────────────────────
#  MIXINS
# ─────────────────────────────────────────────────────────

class TimeStampedModel(models.Model):
    """Abstract base: created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Abstract base: published flag + publish timestamp."""
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from the public site."
    )
    published_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Optional. Set automatically if left blank when publishing."
    )

    class Meta:
        abstract = True


# ─────────────────────────────────────────────────────────
#  SERVICE
# ─────────────────────────────────────────────────────────

class Service(TimeStampedModel, PublishableModel):
    """A service offered by TK MULTIMEDIA."""

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    short_description = models.CharField(
        max_length=220,
        help_text="One-line summary used on cards and previews."
    )
    description = models.TextField(
        help_text="Full description shown on the service detail page."
    )

    cover_image = models.ImageField(
        upload_to="services/covers/",
        blank=True, null=True,
        help_text="Optional. Recommended size: 1200×800."
    )
    icon = models.CharField(
        max_length=40, blank=True,
        help_text="Optional short emoji or code, e.g. 🌐 or 'web'."
    )

    starting_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Optional. Leave blank to hide pricing on the site."
    )
    price_note = models.CharField(
        max_length=120, blank=True,
        help_text="Optional. E.g. 'Starting from' or 'Per project'."
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first."
    )

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tkmedia:service_detail", kwargs={"slug": self.slug})


# ─────────────────────────────────────────────────────────
#  PROJECT
# ─────────────────────────────────────────────────────────

class Project(TimeStampedModel, PublishableModel):
    """A portfolio project."""

    CATEGORY_CHOICES = [
        ("web", "Web Development"),
        ("design", "Graphic Design"),
        ("multimedia", "Multimedia"),
        ("video", "Video"),
        ("branding", "Branding"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="web"
    )

    summary = models.CharField(
        max_length=240,
        help_text="One-line summary for cards."
    )
    description = models.TextField(
        help_text="Full description. Markdown not yet supported — plain text or line breaks."
    )

    cover_image = models.ImageField(
        upload_to="portfolio/covers/",
        blank=True, null=True
    )

    technologies = models.CharField(
        max_length=240, blank=True,
        help_text="Comma-separated. E.g. Django, PostgreSQL, JavaScript."
    )

    completed_on = models.DateField(null=True, blank=True)

    external_url = models.URLField(
        blank=True,
        help_text="Optional live site URL."
    )
    source_url = models.URLField(
        blank=True,
        help_text="Optional source-code URL."
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Featured projects appear on the homepage."
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_featured", "display_order", "-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tkmedia:project_detail", kwargs={"slug": self.slug})

    def technologies_list(self):
        if not self.technologies:
            return []
        return [t.strip() for t in self.technologies.split(",") if t.strip()]


class ProjectImage(TimeStampedModel):
    """An image attached to a Project (gallery)."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="portfolio/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Project image"
        verbose_name_plural = "Project images"

    def __str__(self):
        return f"{self.project.title} — image {self.pk}"
    

# ─────────────────────────────────────────────────────────
#  CONTACT MESSAGE
# ─────────────────────────────────────────────────────────

class ContactMessage(TimeStampedModel):
    """A message submitted through the public contact form."""

    STATUS_NEW = "new"
    STATUS_READ = "read"
    STATUS_REPLIED = "replied"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_READ, "Read"),
        (STATUS_REPLIED, "Replied"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact message"
        verbose_name_plural = "Contact messages"
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.subject[:60]}"

    def short_message(self):
        return self.message[:80] + ("…" if len(self.message) > 80 else "")


# ─────────────────────────────────────────────────────────
#  GALLERY ITEM (public media)
# ─────────────────────────────────────────────────────────

class GalleryItem(TimeStampedModel, PublishableModel):
    """A public image in the gallery — distinct from portfolio projects."""

    CATEGORY_CHOICES = [
        ("design", "Design"),
        ("flyer", "Flyer"),
        ("branding", "Branding"),
        ("photo", "Photography"),
        ("video", "Video Thumbnail"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=140)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="design"
    )
    image = models.ImageField(upload_to="gallery/public/")
    alt_text = models.CharField(
        max_length=200,
        help_text="Describe the image for accessibility and SEO.",
    )
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Gallery item"
        verbose_name_plural = "Gallery items"

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────
#  SKILL
# ─────────────────────────────────────────────────────────

class Skill(TimeStampedModel):
    """A skill or technology displayed on the About page."""

    CATEGORY_CHOICES = [
        ("technical", "Technical"),
        ("creative", "Creative"),
        ("tool", "Tool"),
    ]

    name = models.CharField(max_length=80)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="technical"
    )
    description = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category", "display_order", "name"]
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


# ─────────────────────────────────────────────────────────
#  SITE SETTINGS (singleton)
# ─────────────────────────────────────────────────────────

class SiteSettings(TimeStampedModel):
    """
    Singleton model — always exactly one row.

    Editable from the admin so brand copy, homepage audio,
    and legal text don't require code changes.
    """

    brand_name = models.CharField(max_length=80, default="TK MULTIMEDIA")
    tagline = models.CharField(
        max_length=200,
        default="Building Digital Experiences. Creating Possibilities.",
    )
    homepage_headline = models.CharField(
        max_length=200,
        default="Building Digital Experiences. Creating Possibilities.",
    )
    homepage_intro = models.TextField(
        blank=True,
        help_text="Short paragraph shown under the homepage headline.",
    )
    about_story = models.TextField(blank=True)
    about_philosophy = models.TextField(blank=True)

    contact_email = models.EmailField(default="teakaymultimedia@gmail.com")
    contact_whatsapp = models.CharField(
        max_length=30, default="233531372310",
        help_text="International format, no leading zero, no +.",
    )

    homepage_audio = models.FileField(
        upload_to="audio/",
        blank=True, null=True,
        help_text="Optional. MP3 or M4A recommended. Played only after user clicks play.",
    )
    homepage_audio_transcript = models.TextField(
        blank=True,
        help_text="Transcript shown below the audio player for accessibility.",
    )

    privacy_policy = models.TextField(blank=True)
    terms_of_use = models.TextField(blank=True)

    footer_text = models.CharField(max_length=240, blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        # Enforce singleton
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj