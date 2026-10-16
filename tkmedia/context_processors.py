"""Template context processors for TK MULTIMEDIA."""
from django.conf import settings


def brand(request):
    """Expose brand settings to all templates."""
    return {
        "BRAND_NAME": getattr(settings, "BRAND_NAME", "TK MULTIMEDIA"),
        "BRAND_EMAIL": getattr(settings, "BRAND_EMAIL", "teakaymultimedia@gmail.com"),
        "BRAND_WHATSAPP": getattr(settings, "BRAND_WHATSAPP", "233531372310"),
        "BRAND_TAGLINE": getattr(
            settings, "BRAND_TAGLINE",
            "Building Digital Experiences. Creating Possibilities."
        ),
        "BRAND_WHATSAPP_URL": f"https://wa.me/{getattr(settings, 'BRAND_WHATSAPP', '233531372310')}",
        "BRAND_EMAIL_URL": f"mailto:{getattr(settings, 'BRAND_EMAIL', 'teakaymultimedia@gmail.com')}",
    }


def site_meta(request):
    """Basic SEO meta — expanded in Stage 10."""
    return {
        "SITE_NAME": getattr(settings, "BRAND_NAME", "TK MULTIMEDIA"),
        "SITE_DESCRIPTION": (
            "TK MULTIMEDIA — technology, creativity, and digital innovation. "
            "Web development, multimedia production, digital design, and practical technology solutions."
        ),
    }