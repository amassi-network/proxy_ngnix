from django import forms
from .models import Proxy

class ProxyForm(forms.ModelForm):
    class Meta:
        model = Proxy
        fields = ['domain', 'backend', 'active', 'private_key', 'certificate', 'chain']

    def clean_private_key(self):
        data = self.cleaned_data['private_key']
        if not data.strip().startswith('-----BEGIN'):
            raise forms.ValidationError('Clé privée invalide')
        return data

    def clean_certificate(self):
        data = self.cleaned_data['certificate']
        if not data.strip().startswith('-----BEGIN CERTIFICATE-----'):
            raise forms.ValidationError('Certificat invalide')
        return data

    def clean_chain(self):
        data = self.cleaned_data['chain']
        if not data.strip().startswith('-----BEGIN'):
            raise forms.ValidationError('Chaîne intermédiaire invalide')
        return data
