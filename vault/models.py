# from django.db import models

# # Create your models here.


"""
Private Vault models.

Everything here is strictly for authenticated users. Files are stored
outside the public web root, referenced by random UUIDs, and accessed
only via permission-checked views.
"""
import uuid
import hashlib
from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .storage import PrivateMediaStorage


# ─────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = [
    # Documents
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "csv", "rtf", "odt", "ods", "odp",
    # Archives
    "zip",
    # Images
    "png", "jpg", "jpeg", "gif", "webp", "bmp", "svg",
    # Audio
    "mp3", "wav", "ogg", "m4a", "flac",
    # Video
    "mp4", "mov", "webm", "avi",
    # Code / data
    "json", "xml", "yaml", "yml", "md",
]

MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def private_upload_path(instance, filename):
    """
    Never trust the user-provided filename.
    Generate a random UUID-based path.
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    folder = instance.folder_uid or "root"
    return f"files/{folder}/{uuid.uuid4().hex}.{ext}" if ext else f"files/{folder}/{uuid.uuid4().hex}"


# ─────────────────────────────────────────────────────────
#  FOLDER
# ─────────────────────────────────────────────────────────

class PrivateFolder(models.Model):
    """A folder inside the private vault."""

    name = models.CharField(max_length=200)
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="children",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="vault_folders",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Vault folder"
        verbose_name_plural = "Vault folders"
        indexes = [
            models.Index(fields=["owner", "parent"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("vault:folder_detail", kwargs={"pk": self.pk})

    @property
    def file_count(self):
        return self.files.filter(is_deleted=False).count()

    @property
    def size_bytes(self):
        return self.files.filter(is_deleted=False).aggregate(
            total=models.Sum("size")
        )["total"] or 0

    @property
    def folder_uid(self):
        return self.uid.hex


# ─────────────────────────────────────────────────────────
#  FILE
# ─────────────────────────────────────────────────────────

class PrivateFile(models.Model):
    """An uploaded file inside the private vault."""

    # Identity
    original_name = models.CharField(max_length=300)
    storage_name = models.CharField(
        max_length=300, blank=True,
        help_text="Random internal name — set automatically",
    )
    file = models.FileField(
        upload_to="files/",
        storage=PrivateMediaStorage,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
    )

    # Metadata
    size = models.PositiveBigIntegerField(default=0, help_text="Size in bytes")
    mime_type = models.CharField(max_length=120, blank=True)
    checksum = models.CharField(
        max_length=64, blank=True,
        help_text="SHA-256 checksum"
    )

    # Organization
    folder = models.ForeignKey(
        PrivateFolder, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="files",
    )
    folder_uid = models.CharField(max_length=40, blank=True, editable=False)
    description = models.TextField(blank=True)
    tags = models.CharField(
        max_length=300, blank=True,
        help_text="Comma-separated tags",
    )

    # Ownership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="vault_files",
    )

    # Soft delete (trash)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Vault file"
        verbose_name_plural = "Vault files"
        indexes = [
            models.Index(fields=["owner", "-uploaded_at"]),
            models.Index(fields=["owner", "folder", "is_deleted"]),
        ]

    def __str__(self):
        return self.original_name

    def save(self, *args, **kwargs):
        # Save folder_uid cache from parent folder for stable path generation
        if self.folder:
            self.folder_uid = self.folder.uid.hex
        else:
            self.folder_uid = ""

        # Fill in size + mime + checksum on first save
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except (OSError, ValueError):
                self.size = 0

            # Compute SHA-256 checksum
            if not self.checksum:
                try:
                    h = hashlib.sha256()
                    for chunk in self.file.chunks():
                        h.update(chunk)
                    self.checksum = h.hexdigest()
                    self.file.seek(0)
                except (OSError, ValueError):
                    pass

        super().save(*args, **kwargs)

    @property
    def extension(self):
        return Path(self.original_name).suffix.lower().lstrip(".")

    @property
    def size_display(self):
        return human_size(self.size)

    @property
    def tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def is_image(self):
        return self.extension in {"png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"}

    def soft_delete(self):
        """Move to trash."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """Restore from trash."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def delete(self, *args, **kwargs):
        """Permanently delete the file from disk too."""
        storage = self.file.storage
        name = self.file.name
        super().delete(*args, **kwargs)
        if name and storage.exists(name):
            try:
                storage.delete(name)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────
#  AUDIT LOG
# ─────────────────────────────────────────────────────────

class VaultAuditLog(models.Model):
    """Records sensitive vault operations for security review."""

    ACTION_CHOICES = [
        ("upload", "Upload"),
        ("download", "Download"),
        ("rename", "Rename"),
        ("move", "Move"),
        ("delete", "Move to trash"),
        ("restore", "Restore from trash"),
        ("purge", "Permanent delete"),
        ("folder_create", "Create folder"),
        ("folder_delete", "Delete folder"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="vault_audit_logs",
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    file_name = models.CharField(max_length=300, blank=True)
    file_id = models.PositiveIntegerField(null=True, blank=True)
    folder_id = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Vault audit log"
        verbose_name_plural = "Vault audit logs"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} — {self.user} — {self.action}"


# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────

def human_size(num_bytes):
    """Format bytes as human-readable string."""
    if not num_bytes:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"
