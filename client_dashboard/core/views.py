from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import httpx
from .models import ChatbotConfig

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Cria um ChatbotConfig para o novo usuário com valores padrão
            ChatbotConfig.objects.create(user=user)
            # Loga o usuário automaticamente após o registro
            login(request, user)
            # Redireciona para uma página inicial ou de dashboard (ainda a ser criada)
            # Por enquanto, vamos redirecionar para a página de login
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

from .forms import ChatbotConfigForm

@login_required
def home(request):
    chatbot_config = ChatbotConfig.objects.get(user=request.user)
    return render(request, 'home.html', {'config': chatbot_config})

@login_required
def dashboard(request):
    config = get_object_or_404(ChatbotConfig, user=request.user)
    if request.method == 'POST':
        form = ChatbotConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ChatbotConfigForm(instance=config)
    return render(request, 'dashboard.html', {'form': form})

def chat_embed_view(request, chatbot_id):
    config = get_object_or_404(ChatbotConfig, id=chatbot_id)
    return render(request, 'chat_embed.html', {'config': config, 'chatbot_id': chatbot_id})

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    try:
        # Obter o chatbot_id do header X-Client-ID
        chatbot_id = request.headers.get('X-Client-ID')
        if not chatbot_id:
            return JsonResponse({'error': 'Header X-Client-ID é obrigatório'}, status=400)
        
        # Buscar a configuração do chatbot
        try:
            config = ChatbotConfig.objects.get(id=chatbot_id)
        except ChatbotConfig.DoesNotExist:
            return JsonResponse({'error': 'Chatbot não encontrado'}, status=404)
        
        # Verificar se há webhook configurado
        if not config.webhook_url:
            return JsonResponse({'reply': 'Desculpe, o webhook não está configurado para este chatbot.'}, status=200)
        
        # Obter dados da mensagem
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'Mensagem é obrigatória'}, status=400)
        
        # Enviar para o webhook
        try:
            webhook_response = requests.post(
                config.webhook_url,
                json={'message': message},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            webhook_response.raise_for_status()
            
            # Retornar resposta do webhook
            webhook_data = webhook_response.json()
            return JsonResponse(webhook_data)
            
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'reply': 'Desculpe, não consegui me conectar ao serviço de chat no momento. Tente novamente mais tarde.'
            }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chat_proxy_api_view(request):
    """
    API otimizada para proxy de chat que substitui a lógica do FastAPI.
    
    Recebe:
    - chatbot_id: ID do chatbot no corpo da requisição JSON
    - message: Mensagem do usuário no corpo da requisição JSON
    
    Retorna:
    - JsonResponse com a resposta do webhook do cliente
    """
    try:
        # Validar Content-Type
        if request.content_type != 'application/json':
            return JsonResponse({
                'error': 'Content-Type deve ser application/json'
            }, status=400)
        
        # Parsear dados JSON do corpo da requisição
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Dados JSON inválidos no corpo da requisição'
            }, status=400)
        
        # Extrair chatbot_id e message do corpo da requisição
        chatbot_id = data.get('chatbot_id')
        message = data.get('message')
        
        # Validar parâmetros obrigatórios
        if not chatbot_id:
            return JsonResponse({
                'error': 'chatbot_id é obrigatório no corpo da requisição'
            }, status=400)
        
        if not message:
            return JsonResponse({
                'error': 'message é obrigatória no corpo da requisição'
            }, status=400)
        
        # Buscar configuração do chatbot no banco de dados
        try:
            config = ChatbotConfig.objects.get(id=chatbot_id)
        except ChatbotConfig.DoesNotExist:
            return JsonResponse({
                'error': f'Chatbot com ID {chatbot_id} não encontrado'
            }, status=404)
        
        # Verificar se webhook_url está configurado
        if not config.webhook_url:
            return JsonResponse({
                'error': 'Webhook URL não configurada para este chatbot',
                'chatbot_id': chatbot_id
            }, status=400)
        
        # Preparar payload para o webhook
        webhook_payload = {
            'message': message,
            'chatbot_id': chatbot_id,
            'timestamp': data.get('timestamp')
        }
        
        # Usar httpx para comunicação com o webhook
        try:
            with httpx.Client(timeout=30.0) as client:
                webhook_response = client.post(
                    config.webhook_url,
                    json=webhook_payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Django-Chat-Proxy/1.0'
                    }
                )
                
                # Verificar status da resposta
                webhook_response.raise_for_status()
                
                # Tentar parsear resposta JSON do webhook
                try:
                    webhook_data = webhook_response.json()
                    
                    # Garantir que sempre há um campo 'reply' na resposta
                    if 'reply' not in webhook_data:
                        if 'mensagem' in webhook_data:
                            webhook_data['reply'] = webhook_data['mensagem']
                        elif 'message' in webhook_data:
                            webhook_data['reply'] = webhook_data['message']
                        elif 'response' in webhook_data:
                            webhook_data['reply'] = webhook_data['response']
                        else:
                            # Se não encontrar nenhum campo conhecido, usar o primeiro valor string
                            for key, value in webhook_data.items():
                                if isinstance(value, str) and value.strip():
                                    webhook_data['reply'] = value
                                    break
                            else:
                                webhook_data['reply'] = 'Resposta recebida mas formato não reconhecido.'
                    
                except json.JSONDecodeError:
                    # Se não for JSON válido, retornar texto como resposta
                    webhook_data = {
                        'reply': webhook_response.text.strip() or 'Resposta vazia do webhook.',
                        'status': 'success'
                    }
                
                # Retornar resposta do webhook como JsonResponse
                return JsonResponse(webhook_data, status=200)
                
        except httpx.TimeoutException:
            return JsonResponse({
                'error': 'Timeout ao conectar com o webhook',
                'reply': 'Desculpe, o serviço está demorando para responder. Tente novamente.'
            }, status=408)
            
        except httpx.HTTPStatusError as e:
            return JsonResponse({
                'error': f'Erro HTTP do webhook: {e.response.status_code}',
                'reply': 'Desculpe, houve um problema com o serviço de chat. Tente novamente mais tarde.'
            }, status=502)
            
        except httpx.RequestError as e:
            return JsonResponse({
                'error': f'Erro de conexão com webhook: {str(e)}',
                'reply': 'Desculpe, não consegui me conectar ao serviço de chat. Verifique sua conexão.'
            }, status=503)
            
    except Exception as e:
        # Log do erro para debugging (em produção, usar logging adequado)
        print(f"Erro interno na chat_proxy_api_view: {str(e)}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'reply': 'Desculpe, ocorreu um erro interno. Tente novamente mais tarde.'
        }, status=500)
