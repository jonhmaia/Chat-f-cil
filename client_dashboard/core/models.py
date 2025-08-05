import uuid
from django.db import models
from django.contrib.auth.models import User

class ChatbotConfig(models.Model):
    """
    Modelo para armazenar as configurações personalizadas do chatbot para cada usuário.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chatbot_config')
    webhook_url = models.URLField(max_length=200, blank=True, help_text="A URL para a qual enviaremos os eventos de chat.")
    primary_color = models.CharField(max_length=7, default='#007BFF', help_text="Cor principal do chat em hexadecimal (ex: #007BFF).")
    welcome_message = models.CharField(max_length=255, default='Olá! Como posso ajudar?', help_text="A primeira mensagem que o bot envia.")

    def __str__(self):
        return f"Configuração do Chatbot para {self.user.username}"
