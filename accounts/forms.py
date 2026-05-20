# accounts/forms.py
from django.utils.translation import gettext_lazy as _
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UsernameField,
    AuthenticationForm,
    PasswordChangeForm,
)
from django.conf import settings
from academia.models import Program

from .models import *


def _portal_password_widget():
    return forms.PasswordInput(
        attrs={
            "class": "catalog-toolbar__input",
            "autocomplete": "off",
        }
    )


class PortalPasswordChangeForm(PasswordChangeForm):
    """Cambio de contraseña dentro del portal (requiere la actual)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = _("Contraseña actual")
        self.fields["new_password1"].label = _("Nueva contraseña")
        self.fields["new_password2"].label = _("Confirmar nueva contraseña")
        self.fields["old_password"].widget = _portal_password_widget()
        self.fields["old_password"].widget.attrs["autocomplete"] = "current-password"
        self.fields["new_password1"].widget = _portal_password_widget()
        self.fields["new_password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["new_password2"].widget = _portal_password_widget()
        self.fields["new_password2"].widget.attrs["autocomplete"] = "new-password"
        self.fields["old_password"].help_text = None
        for name in ("new_password1", "new_password2"):
            if self.fields[name].help_text:
                self.fields[name].help_text = _(
                    "Mínimo 8 caracteres. No use una contraseña muy común ni solo números."
                )


class EasyLearnAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Usuario"),
        widget=forms.TextInput(
            attrs={
                "class": "el-login__input",
                "placeholder": "Usuario o correo",
                "autocomplete": "username",
                "autocapitalize": "none",
            }
        ),
    )
    password = forms.CharField(
        label=_("Contraseña"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "el-login__input",
                "placeholder": "Contraseña",
                "autocomplete": "current-password",
            }
        ),
    )


class SiteLeadForm(forms.Form):
    """Correo desde el CTA del home (solicitud de información)."""

    correo = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "el-home-cta__input",
                "placeholder": "tu@universidad.edu",
                "autocomplete": "email",
            }
        ),
    )


class SiteContactForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre completo",
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "el-contact-field",
                "placeholder": "Ej. María González",
            }
        ),
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "el-contact-field",
                "placeholder": "tu@correo.edu",
            }
        ),
    )
    asunto = forms.CharField(
        label="Asunto",
        max_length=160,
        widget=forms.TextInput(
            attrs={
                "class": "el-contact-field",
                "placeholder": "Demo institucional",
            }
        ),
    )
    mensaje = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(
            attrs={
                "class": "el-contact-field el-contact-field--box",
                "rows": 5,
                "placeholder": "Cuéntenos sobre su institución o consulta…",
            }
        ),
    )


class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ("username",)
        field_classes = {"username": UsernameField}


# form for editing a user object
class StudentUpdateForm(forms.ModelForm):
    academic_program = forms.ModelChoiceField(
        queryset=Program.objects.order_by("name"),
        required=False,
        label="Carrera / programa",
        empty_label="Sin carrera asignada",
    )
    academic_semester = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        label="Semestre académico",
    )

    class Meta:
        model = Student
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "academic_program",
            "academic_semester",
        ]

    def clean_email(self):
        data = self.cleaned_data["email"]
        qs = Student.objects.exclude(id=self.instance.id).filter(email=data)
        if qs.exists():
            raise forms.ValidationError("Email already in use.")
        return data


# form for editing a user object
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["degree", "date_of_birth", "year", "photo"]
        widgets = {
            "date_of_birth": DatePickerInput(),
        }


# class DeleteAccountForm(forms.ModelForm):
#     confirm_delete = forms.BooleanField(label="Confirm deletion", required=True)

#     class Meta:
#         model = Student
#         fields = []
