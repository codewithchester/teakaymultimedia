"""Forms used in the custom dashboard."""
from django import forms
from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    """Edit SiteSettings from the dashboard."""

    class Meta:
        model = SiteSettings
        fields = [
            "brand_name", "tagline", "footer_text",
            "homepage_headline", "homepage_intro",
            "homepage_audio", "homepage_audio_transcript",
            "about_story", "about_philosophy",
            "contact_email", "contact_whatsapp",
            "privacy_policy", "terms_of_use",
        ]
        widgets = {
            "brand_name": forms.TextInput(attrs={"class": "dash-input"}),
            "tagline": forms.TextInput(attrs={"class": "dash-input"}),
            "footer_text": forms.TextInput(attrs={"class": "dash-input"}),
            "homepage_headline": forms.TextInput(attrs={"class": "dash-input"}),
            "homepage_intro": forms.Textarea(attrs={"class": "dash-input", "rows": 3}),
            "homepage_audio": forms.ClearableFileInput(attrs={"class": "dash-input"}),
            "homepage_audio_transcript": forms.Textarea(attrs={"class": "dash-input", "rows": 4}),
            "about_story": forms.Textarea(attrs={"class": "dash-input", "rows": 5}),
            "about_philosophy": forms.Textarea(attrs={"class": "dash-input", "rows": 4}),
            "contact_email": forms.EmailInput(attrs={"class": "dash-input"}),
            "contact_whatsapp": forms.TextInput(attrs={"class": "dash-input"}),
            "privacy_policy": forms.Textarea(attrs={"class": "dash-input", "rows": 12}),
            "terms_of_use": forms.Textarea(attrs={"class": "dash-input", "rows": 12}),
        }