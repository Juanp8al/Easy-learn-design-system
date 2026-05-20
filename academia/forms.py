"""Formularios del portal administrador (creación con estilo EasyLearn)."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify

from academia.models import AcademicPeriod, Enrollment, Offering, Program
from accounts.models import Student

PORTAL_INPUT_CLASS = "catalog-toolbar__input"
PORTAL_SELECT_CLASS = "select-ui catalog-toolbar__select"
PORTAL_CHECK_CLASS = "portal-admin-form__check"


def _text(attrs=None):
    base = {"class": PORTAL_INPUT_CLASS}
    if attrs:
        base.update(attrs)
    return base


def _select(attrs=None):
    base = {"class": PORTAL_SELECT_CLASS}
    if attrs:
        base.update(attrs)
    return base


class StudentAdminCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, widget=forms.TextInput(attrs=_text()))
    last_name = forms.CharField(label="Apellido", max_length=150, widget=forms.TextInput(attrs=_text()))
    email = forms.EmailField(label="Correo", required=False, widget=forms.EmailInput(attrs=_text()))
    role = forms.ChoiceField(
        label="Rol",
        choices=Student.Role.choices,
        widget=forms.Select(attrs=_select()),
    )
    academic_program = forms.ModelChoiceField(
        label="Carrera / programa",
        queryset=Program.objects.order_by("name"),
        required=False,
        empty_label="— Sin carrera —",
        widget=forms.Select(attrs=_select()),
    )
    academic_semester = forms.IntegerField(
        label="Semestre académico",
        required=False,
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs=_text()),
    )
    is_active = forms.BooleanField(
        label="Cuenta activa",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": PORTAL_CHECK_CLASS}),
    )

    class Meta(UserCreationForm.Meta):
        model = Student
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "academic_program",
            "academic_semester",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["username"].widget.attrs.update(
            _text({"placeholder": "Ej. jramirez", "autocomplete": "username"})
        )
        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].help_text = "Mínimo 8 caracteres."
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={**_text(), "autocomplete": "new-password"}
        )
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].help_text = ""
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={**_text(), "autocomplete": "new-password"}
        )


class ProgramAdminCreateForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ("name", "code")
        labels = {
            "name": "Nombre de la carrera",
            "code": "Código",
        }
        widgets = {
            "name": forms.TextInput(attrs=_text({"placeholder": "Ej. Ingeniería de sistemas"})),
            "code": forms.TextInput(attrs=_text({"placeholder": "Ej. IS"})),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        base = slugify(instance.name) or "programa"
        slug = base
        n = 1
        while Program.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        instance.slug = slug
        if commit:
            instance.save()
        return instance


class AcademicPeriodAdminCreateForm(forms.ModelForm):
    class Meta:
        model = AcademicPeriod
        fields = ("name", "starts_on", "ends_on", "is_current")
        widgets = {
            "name": forms.TextInput(attrs=_text({"placeholder": "Ej. 2026-1"})),
            "starts_on": forms.DateInput(attrs={**_text(), "type": "date"}),
            "ends_on": forms.DateInput(attrs={**_text(), "type": "date"}),
            "is_current": forms.CheckboxInput(attrs={"class": PORTAL_CHECK_CLASS}),
        }


class OfferingAdminCreateForm(forms.ModelForm):
    class Meta:
        model = Offering
        fields = (
            "program",
            "period",
            "name",
            "code",
            "semester",
            "group",
            "credits",
            "teacher",
        )
        widgets = {
            "program": forms.Select(attrs=_select()),
            "period": forms.Select(attrs=_select()),
            "name": forms.TextInput(attrs=_text({"placeholder": "Ej. Algoritmos y estructuras de datos"})),
            "code": forms.TextInput(attrs=_text({"placeholder": "Ej. AED-301"})),
            "semester": forms.NumberInput(attrs=_text({"min": "1", "max": "12", "placeholder": "1"})),
            "group": forms.TextInput(attrs=_text({"placeholder": "A"})),
            "credits": forms.NumberInput(attrs=_text({"min": "1", "max": "10", "placeholder": "3"})),
            "teacher": forms.Select(attrs=_select()),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["program"].queryset = Program.objects.order_by("name")
        self.fields["program"].empty_label = "Seleccione carrera"
        self.fields["period"].queryset = AcademicPeriod.objects.order_by("-name")
        self.fields["period"].empty_label = "Seleccione período"
        self.fields["teacher"].queryset = Student.objects.filter(
            role=Student.Role.TEACHER, is_active=True
        ).order_by("first_name", "username")
        self.fields["teacher"].required = False
        self.fields["teacher"].empty_label = "— Sin docente —"


class EnrollmentAdminCreateForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ("student", "offering", "status")
        widgets = {
            "student": forms.Select(attrs=_select()),
            "offering": forms.Select(attrs=_select()),
            "status": forms.Select(attrs=_select()),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.filter(
            role=Student.Role.STUDENT, is_active=True
        ).order_by("first_name", "username")
        self.fields["student"].empty_label = "Seleccione estudiante"
        self.fields["offering"].queryset = Offering.objects.select_related(
            "program", "period"
        ).order_by("-period__name", "program__name", "code")
        self.fields["offering"].empty_label = "Seleccione curso"
        self.fields["offering"].label_from_instance = (
            lambda o: f"{o.code} · {o.name} ({o.period.name})"
        )
        self.fields["student"].label_from_instance = (
            lambda u: u.get_full_name() or u.username
        )
