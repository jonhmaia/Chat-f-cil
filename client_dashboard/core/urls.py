from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.home, name='home'),
    path('chatbots/', views.chatbot_list, name='chatbot_list'),
    path('chatbots/create/', views.create_chatbot, name='create_chatbot'),
    path('chatbots/<uuid:chatbot_id>/dashboard/', views.dashboard, name='dashboard'),
    path('chatbots/<uuid:chatbot_id>/delete/', views.delete_chatbot, name='delete_chatbot'),
    path('embed/<uuid:chatbot_id>/', views.chat_embed_view, name='chat_embed'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/v1/chat/', views.chat_proxy_api_view, name='chat_proxy_api'),
]