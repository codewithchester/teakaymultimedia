"""
Private storage backend for vault files.

Files are stored OUTSIDE the public media root. They are NEVER served
directly by the web server — access is only via authenticated views.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateMediaStorage(FileSystemStorage):
    """
    Files stored outside the public media root with restrictive permissions.

    - location  -> settings.PRIVATE_MEDIA_ROOT (e.g. media/private/)
    - base_url  -> None (never serve directly)
    - file mode -> 0o600 (owner read/write only)
    """
    def __init__(self):
        super().__init__(
            location=str(settings.PRIVATE_MEDIA_ROOT),
            base_url=None,
            file_permissions_mode=0o600,
            directory_permissions_mode=0o700,
        )