"""Forms for the private vault."""
from django import forms

from .models import (
    PrivateFolder,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    MAX_FILE_SIZE_BYTES,
)


class VaultUploadForm(forms.Form):
    """Upload a file to the vault."""

    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            "class": "dash-input",
            "accept": ", ".join(f".{e}" for e in ALLOWED_EXTENSIONS),
        }),
        help_text=f"Max size: {MAX_FILE_SIZE_MB} MB.",
    )
    folder = forms.ModelChoiceField(
        queryset=PrivateFolder.objects.none(),
        required=False,
        empty_label="— No folder (root) —",
        widget=forms.Select(attrs={"class": "dash-select"}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "dash-input",
            "rows": 3,
            "placeholder": "Optional. What is this file for?",
        }),
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "dash-input",
            "placeholder": "Comma-separated, e.g. client-a, contract, 2026",
        }),
    )

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields["folder"].queryset = PrivateFolder.objects.filter(owner=owner)

    def clean_file(self):
        f = self.cleaned_data["file"]
        if f.size > MAX_FILE_SIZE_BYTES:
            raise forms.ValidationError(
                f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB "
                f"(your file is {round(f.size / 1024 / 1024, 1)} MB)."
            )
        return f


class FolderCreateForm(forms.Form):
    """Create a new folder."""

    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "dash-input",
            "placeholder": "Folder name",
        }),
    )
    parent = forms.ModelChoiceField(
        queryset=PrivateFolder.objects.none(),
        required=False,
        empty_label="— Root level —",
        widget=forms.Select(attrs={"class": "dash-select"}),
    )

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields["parent"].queryset = PrivateFolder.objects.filter(owner=owner)


class FileEditForm(forms.Form):
    """Edit file metadata (name, description, tags, folder)."""

    original_name = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={"class": "dash-input"}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "dash-input",
            "rows": 4,
            "placeholder": "Optional. Notes about this file.",
        }),
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "dash-input",
            "placeholder": "Comma-separated tags",
        }),
    )
    folder = forms.ModelChoiceField(
        queryset=PrivateFolder.objects.none(),
        required=False,
        empty_label="— No folder (root) —",
        widget=forms.Select(attrs={"class": "dash-select"}),
    )

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields["folder"].queryset = PrivateFolder.objects.filter(owner=owner)