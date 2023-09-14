from django import forms
from django.forms import ClearableFileInput
from .models import UploadBook


class BookUploader(forms.ModelForm):
    class Meta:
        model = UploadBook
        fields = ['book_file']
        widgets = {
            'book_file': ClearableFileInput(attrs={'multiple': True}),
        }
