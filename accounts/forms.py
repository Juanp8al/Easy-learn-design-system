# accounts/forms.py
from django.utils.translation import gettext_lazy as _
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UsernameField,
    AuthenticationForm,
)
from django.conf import settings
from academia.models import Program

from .models import *


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
