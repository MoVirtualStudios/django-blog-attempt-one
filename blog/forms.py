from django import forms
import time

from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Comment
from .models import Post


class CommentForm(forms.ModelForm):

    website = forms.CharField(required=False, widget=forms.HiddenInput,)
    timestamp = forms.CharField(required=False, widget=forms.HiddenInput,)

    class Meta:
        model = Comment

        fields = (
            "name",
            "email",
            "body",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your email",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "formm-control",
                    "rows": 5,
                    "placeholder": "Write your comment...",
                }
            ),
        }


    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name.strip()) < 2:
            raise forms.ValidationError("Please enter your name.")
        return name.strip()

    def clean_email(self):
        email = self.cleaned_data["email"]
        return email.lower()

    def clean_body(self):
        body = self.cleaned_data["body"]

        if len(body.strip()) < 10:
            raise forms.ValidationError(
                "Your comment is too short. Please write atleast 10 characters."
            )
        return body.strip()

    def clean_website(self):
        website = self.cleaned_data["website"]
        if website:
            raise forms.ValidationError(
                "Spam detected."
            )
        return website

    def clean_timestamp(self):
        timestamp = self.cleaned_data["timestamp"]
        if timestamp:
            elapsed = time.time() - float(timestamp)
            if elapsed < 3:
                raise forms.ValidationError("Please take a moment before submitting.")
        return timestamp


class PostForm(forms.ModelForm):

    class Meta:

        model = Post

        fields = (
            "title",
            "slug",
            "category",
            "tags",
            "featured_image",
            "excerpt",
            "body",
            "status",
        )

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "excerpt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "body": CKEditor5Widget(
                config_name="default",
                
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["category"].widget.attrs.update(
            {
                "class": "form-select",
            }
        )

        self.fields["tags"].widget.attrs.update(
            {
                "class": "form-select",
            }
        )

        self.fields["featured_image"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


class ContactForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your name",
            },
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your email address",
            },
        ),
    )

    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Message subject",
            },
        ),
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Write your message here",
                "rows": 6,
            },
        ),
    )