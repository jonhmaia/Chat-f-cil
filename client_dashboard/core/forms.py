from django import forms
from .models import ChatbotConfig

class ChatbotConfigForm(forms.ModelForm):
    class Meta:
        model = ChatbotConfig
        fields = ['webhook_url', 'primary_color', 'welcome_message']