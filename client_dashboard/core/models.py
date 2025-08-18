import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatbotConfig(models.Model):
    """
    Modelo para armazenar as configurações personalizadas dos chatbots para cada usuário.
    Cada usuário pode ter múltiplos chatbots.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbots')
    name = models.CharField(max_length=100, default='Meu Chatbot', help_text="Nome do chatbot para identificação")
    webhook_url = models.URLField(max_length=200, blank=True, help_text="A URL para a qual enviaremos os eventos de chat.")
    primary_color = models.CharField(max_length=7, default='#007BFF', help_text="Cor principal do chat em hexadecimal (ex: #007BFF).")
    welcome_message = models.CharField(max_length=255, default='Olá! Como posso ajudar?', help_text="A primeira mensagem que o bot envia.")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Configuração do Chatbot'
        verbose_name_plural = 'Configurações dos Chatbots'

    def __str__(self):
        return f"{self.name} - {self.user.username}"
