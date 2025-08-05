# API de Proxy do Django - Documentação

## Visão Geral

A nova API de proxy do Django (`chat_proxy_api_view`) substitui a lógica do FastAPI anterior, fornecendo uma solução nativa e otimizada para o Django.

## Endpoint

```
POST /api/v1/chat/
```

## Características

### ✅ Implementado

- **Otimizada para Django**: Usa decoradores nativos do Django (`@csrf_exempt`, `@require_http_methods`)
- **Validação rigorosa**: Verifica Content-Type e estrutura JSON
- **Comunicação com httpx**: Biblioteca moderna para requisições HTTP assíncronas
- **Tratamento de erros robusto**: Diferentes códigos de status para diferentes tipos de erro
- **Timeout configurável**: 30 segundos para evitar travamentos
- **Headers personalizados**: User-Agent identificando o proxy Django

### 🔧 Funcionalidades

1. **Recebe requisições POST com JSON**
2. **Extrai `chatbot_id` e `message` do corpo da requisição**
3. **Busca `webhook_url` no banco de dados usando o `chatbot_id`**
4. **Repassa a mensagem para o webhook do cliente usando httpx**
5. **Retorna a resposta do webhook como JsonResponse**

## Formato da Requisição

### Headers Obrigatórios
```
Content-Type: application/json
```

### Corpo da Requisição
```json
{
  "chatbot_id": 1,
  "message": "Olá, como você está?",
  "timestamp": "2024-01-15T10:30:00Z"  // Opcional
}
```

## Respostas

### ✅ Sucesso (200)
```json
{
  "reply": "Olá! Estou bem, obrigado por perguntar!",
  "status": "success"
}
```

### ❌ Erros Possíveis

#### 400 - Bad Request
```json
{
  "error": "Content-Type deve ser application/json"
}
```

```json
{
  "error": "chatbot_id é obrigatório no corpo da requisição"
}
```

```json
{
  "error": "message é obrigatória no corpo da requisição"
}
```

```json
{
  "error": "Webhook URL não configurada para este chatbot",
  "chatbot_id": 1
}
```

#### 404 - Not Found
```json
{
  "error": "Chatbot com ID 1 não encontrado"
}
```

#### 408 - Timeout
```json
{
  "error": "Timeout ao conectar com o webhook",
  "reply": "Desculpe, o serviço está demorando para responder. Tente novamente."
}
```

#### 502 - Bad Gateway
```json
{
  "error": "Erro HTTP do webhook: 500",
  "reply": "Desculpe, houve um problema com o serviço de chat. Tente novamente mais tarde."
}
```

#### 503 - Service Unavailable
```json
{
  "error": "Erro de conexão com webhook: Connection refused",
  "reply": "Desculpe, não consegui me conectar ao serviço de chat. Verifique sua conexão."
}
```

## Exemplo de Uso

### Python (requests)
```python
import requests
import json

url = "http://127.0.0.1:8000/api/v1/chat/"
data = {
    "chatbot_id": 1,
    "message": "Olá, como você está?"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
```

### JavaScript (fetch)
```javascript
fetch('http://127.0.0.1:8000/api/v1/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    chatbot_id: 1,
    message: 'Olá, como você está?'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Erro:', error));
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "chatbot_id": 1,
    "message": "Olá, como você está?"
  }'
```

## Melhorias em Relação ao FastAPI

1. **Integração Nativa**: Totalmente integrada ao Django, sem dependências externas
2. **Validação Robusta**: Validação de Content-Type e estrutura JSON
3. **Tratamento de Erros**: Códigos de status HTTP específicos para cada tipo de erro
4. **Performance**: Uso do httpx para comunicação assíncrona
5. **Manutenibilidade**: Código mais limpo e organizado
6. **Segurança**: Uso de decoradores Django para controle de métodos HTTP

## Configuração Necessária

1. **Instalar httpx**: `pip install httpx`
2. **Configurar webhook_url**: Cada chatbot deve ter um webhook_url configurado no banco
3. **Testar conectividade**: Verificar se os webhooks estão acessíveis

## Monitoramento

A API inclui logs de erro para debugging. Em produção, recomenda-se configurar um sistema de logging adequado para monitorar:

- Erros de conexão com webhooks
- Timeouts
- Erros de parsing JSON
- Chatbots não encontrados

## Status da Migração

✅ **Concluído**:
- Implementação da nova view `chat_proxy_api_view`
- Rota `/api/v1/chat/` configurada
- Testes básicos realizados
- Documentação criada

🔄 **Próximos Passos**:
- Criar chatbots de teste no banco de dados
- Configurar webhooks de teste
- Testes de integração completos
- Deploy em produção