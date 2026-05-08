from django import forms
from .models import Asset
from locale_or_translations.translations import get_translations


def key_from_value(prefix, value):
    return f"{prefix}_{value.lower().replace(' ', '_')}"


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, lang="en", **kwargs):
        super().__init__(*args, **kwargs)
        tr = get_translations(lang)
        self.fields["username"].label = tr["username"]
        self.fields["password"].label = tr["password"]
        self.fields["username"].widget.attrs.update({"placeholder": tr["username"], "autocomplete": "username"})
        self.fields["password"].widget.attrs.update({"placeholder": tr["password"], "autocomplete": "current-password"})


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "asset_type",
            "operating_system",
            "software_name",
            "current_version",
            "latest_version",
            "patch_status",
            "criticality",
            "last_update",
            "notes",
        ]
        widgets = {
            "last_update": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, lang="en", **kwargs):
        super().__init__(*args, **kwargs)
        tr = get_translations(lang)

        labels = {
            "name": tr["asset_name"],
            "asset_type": tr["asset_type"],
            "operating_system": tr["operating_system"],
            "software_name": tr["software_name"],
            "current_version": tr["current_version"],
            "latest_version": tr["latest_version"],
            "patch_status": tr["patch_status"],
            "criticality": tr["criticality"],
            "last_update": tr["last_update"],
            "notes": tr["notes"],
        }

        for field_name, label in labels.items():
            self.fields[field_name].label = label
            self.fields[field_name].widget.attrs.update({"placeholder": label})

        self.fields["asset_type"].choices = [
            (value, tr.get(key_from_value("asset_type", value), label))
            for value, label in Asset.AssetType.choices
        ]
        self.fields["patch_status"].choices = [
            (value, tr.get(key_from_value("status", value), label))
            for value, label in Asset.PatchStatus.choices
        ]
        self.fields["criticality"].choices = [
            (value, tr.get(key_from_value("criticality", value), label))
            for value, label in Asset.Criticality.choices
        ]

    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get("current_version")
        latest = cleaned_data.get("latest_version")
        if current and latest and len(current) > 40:
            self.add_error("current_version", "Version value is too long.")
        if latest and len(latest) > 40:
            self.add_error("latest_version", "Version value is too long.")
        return cleaned_data
