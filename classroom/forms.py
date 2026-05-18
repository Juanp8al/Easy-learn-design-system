from django import forms

from classroom.models import Announcement, Forum, Grade


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("offering", "week", "title", "content", "priority")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
            "week": forms.Select(attrs={"class": "catalog-toolbar__input"}),
        }


class ForumStatusForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ("status",)


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ("score", "feedback")
        widgets = {
            "feedback": forms.Textarea(attrs={"rows": 3}),
            "score": forms.NumberInput(attrs={"step": "0.1", "min": "0", "max": "5"}),
        }
