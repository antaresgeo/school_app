from django import forms
from .models import Import


class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = ['document']

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['document'].required = True
