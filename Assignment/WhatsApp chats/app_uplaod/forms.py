from django import forms
from .models import *

class WhatsAppForm(forms.ModelForm):

    class Meta():
        model = WhatsApp
        fields = ['upload_file']
