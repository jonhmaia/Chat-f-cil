from django import forms
from .models import ChatbotConfig

class ChatbotConfigForm(forms.ModelForm):
    class Meta:
        model = ChatbotConfig
        fields = ['name', 'webhook_url', 'primary_color', 'welcome_message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Atendimento Vendas'}),
            'webhook_url': forms.URLInput(attrs={'placeholder': 'https://sua-api.com/webhook'}),
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'welcome_message': forms.TextInput(attrs={'placeholder': 'Olá! Como posso ajudar?'}),
        }