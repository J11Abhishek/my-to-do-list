
from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        required=True,
        error_messages={
            "required": "Please enter a task title.",
            "max_length": "The title cannot exceed 200 characters.",
        },
    )

    class Meta:
        model = Task
        fields = ["title", "description", "notification_email"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "What needs to get done?",
                "class": "form-control",
                "maxlength": "200",
            }),
            "notification_email": forms.EmailInput(attrs={
                "placeholder": "you@example.com (optional)",
                "class": "form-control",
                "autocomplete": "email",
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Add some details (optional)",
                "class": "form-control",
                "rows": 4,
            }),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError("Please enter a task title.")

        return title
