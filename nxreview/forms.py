from django import forms


class ConflictResolutionForm(forms.Form):
    btn = forms.CharField()