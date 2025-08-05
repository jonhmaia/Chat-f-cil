from django.contrib import admin
from .models import ChatbotConfig

@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'webhook_url', 'primary_color', 'welcome_message')
    search_fields = ('user__username', 'webhook_url')
    list_filter = ('primary_color',)
