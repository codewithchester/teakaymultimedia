"""Public-facing forms for TK MULTIMEDIA."""
from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Contact form with honeypot spam protection.

    The 'website' field is hidden from real users via CSS.
    Bots often fill every field — this catches them.
    """

    # Honeypot — must stay empty
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "autocomplete": "off",
            "tabindex": "-1",
            "class": "hp-field",
        }),
        label="",
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Your full name",
                "autocomplete": "name",
                "required": True,
                "maxlength": 120,
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "you@example.com",
                "autocomplete": "email",
                "required": True,
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Optional phone number",
                "autocomplete": "tel",
                "maxlength": 40,
            }),
            "subject": forms.TextInput(attrs={
                "placeholder": "What is this about?",
                "required": True,
                "maxlength": 200,
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Tell me about your project…",
                "rows": 6,
                "required": True,
            }),
        }

    def clean_website(self):
        """Honeypot: if filled, treat as spam."""
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Please write at least 10 characters.")
        if len(message) > 5000:
            raise forms.ValidationError("Message is too long (max 5000 characters).")
        return message

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name