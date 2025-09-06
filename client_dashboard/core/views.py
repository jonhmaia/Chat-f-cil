from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import httpx
from .models import ChatbotConfig

def landing_page(request):
    """Landing page do BeckerChat"""
    return render(request, 'landing.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Cria um ChatbotConfig inicial para o novo usuário
            ChatbotConfig.objects.create(
                user=user,
                name='Meu Primeiro Chatbot'
            )
            # Loga o usuário automaticamente após o registro
            login(request, user)
            # Redireciona para a lista de chatbots
            return redirect('chatbot_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

from .forms import ChatbotConfigForm

@login_required
def home(request):
    # Redireciona para a lista de chatbots
    return redirect('chatbot_list')

@login_required
def chatbot_list(request):
    """Lista todos os chatbots do usuário"""
    chatbots = ChatbotConfig.objects.filter(user=request.user)
    return render(request, 'chatbot_list.html', {'chatbots': chatbots})

@login_required
def create_chatbot(request):
    """Cria um novo chatbot"""
    if request.method == 'POST':
        form = ChatbotConfigForm(request.POST)
        if form.is_valid():
            chatbot = form.save(commit=False)
            chatbot.user = request.user
            chatbot.save()
            return redirect('dashboard', chatbot_id=chatbot.id)
    else:
        form = ChatbotConfigForm()
    return render(request, 'create_chatbot.html', {'form': form})

@login_required
def dashboard(request, chatbot_id):
    """Dashboard para personalizar um chatbot específico"""
    config = get_object_or_404(ChatbotConfig, id=chatbot_id, user=request.user)
    if request.method == 'POST':
        print(f"DEBUG: Requisição POST recebida para chatbot {chatbot_id}")
        print(f"DEBUG: Dados POST: {dict(request.POST)}")
        print(f"DEBUG: Content-Type: {request.content_type}")
        
        # Check if it's an AJAX request for real-time updates
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax and ('primary_color' in request.POST or 'welcome_message' in request.POST or 'webhook_url' in request.POST):
            print("DEBUG: Detectada requisição AJAX para atualização em tempo real")
            try:
                # Update only the specific fields for real-time customization
                if 'primary_color' in request.POST:
                    print(f"DEBUG: Atualizando primary_color: {request.POST['primary_color']}")
                    config.primary_color = request.POST['primary_color']
                if 'welcome_message' in request.POST:
                    print(f"DEBUG: Atualizando welcome_message: {request.POST['welcome_message']}")
                    config.welcome_message = request.POST['welcome_message']
                if 'webhook_url' in request.POST:
                    print(f"DEBUG: Atualizando webhook_url: {request.POST['webhook_url']}")
                    config.webhook_url = request.POST['webhook_url']
                config.save()
                print("DEBUG: Configurações salvas com sucesso!")
                return JsonResponse({'success': True, 'message': 'Configurações salvas com sucesso!'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            # Regular form submission
            form = ChatbotConfigForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                return redirect('chatbot_list')
    else:
        form = ChatbotConfigForm(instance=config)
    return render(request, 'dashboard.html', {'form': form, 'chatbot': config})

@login_required
def delete_chatbot(request, chatbot_id):
    """View para excluir um chatbot específico"""
    chatbot = get_object_or_404(ChatbotConfig, id=chatbot_id, user=request.user)
    
    if request.method == 'POST':
        # Verificar se o usuário tem pelo menos um chatbot restante
        user_chatbots_count = ChatbotConfig.objects.filter(user=request.user).count()
        
        if user_chatbots_count <= 1:
            messages.error(request, 'Você deve ter pelo menos um chatbot. Não é possível excluir o último chatbot.')
            return redirect('chatbot_list')
        
        chatbot_name = chatbot.name
        chatbot.delete()
        messages.success(request, f'Chatbot "{chatbot_name}" foi excluído com sucesso.')
        return redirect('chatbot_list')
    
    # Se não for POST, redirecionar para a lista
    return redirect('chatbot_list')

def chat_embed_view(request, chatbot_id):
    config = get_object_or_404(ChatbotConfig, id=chatbot_id)
    
    # Allow dynamic override of config values for preview
    preview_config = {
        'primary_color': request.GET.get('primary_color', config.primary_color),
        'welcome_message': request.GET.get('welcome_message', config.welcome_message),
        'name': config.name,
        'id': config.id
    }
    
    return render(request, 'chat_embed.html', {'config': preview_config, 'chatbot_id': chatbot_id})

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
