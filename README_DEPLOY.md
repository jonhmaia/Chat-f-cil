# Deploy no Railway - Chat Fácil

## Arquivos de Configuração Criados

Os seguintes arquivos foram criados para preparar a aplicação para deploy no Railway:

- `requirements.txt` - Dependências Python
- `runtime.txt` - Versão do Python
- `Procfile` - Comando de inicialização
- `railway.toml` - Configurações específicas do Railway
- `.env.example` - Exemplo de variáveis de ambiente

## Passos para Deploy

### 1. Preparar o Repositório
```bash
git init
git add .
git commit -m "Preparar para deploy no Railway"
```

### 2. Conectar ao Railway
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha este repositório

### 3. Configurar Variáveis de Ambiente
No painel do Railway, adicione as seguintes variáveis:

- `SECRET_KEY`: Uma chave secreta segura para Django
- `DEBUG`: `False` (para produção)
- `DATABASE_URL`: Será configurada automaticamente pelo Railway

### 4. Adicionar Banco de Dados
1. No painel do Railway, clique em "+ New"
2. Selecione "Database" > "PostgreSQL"
3. O Railway conectará automaticamente ao Django

### 5. Deploy Automático
O Railway detectará automaticamente:
- `Procfile` para comando de inicialização
- `requirements.txt` para instalar dependências
- `runtime.txt` para versão do Python

## Configurações Implementadas

### Segurança
- `DEBUG = False` em produção
- `SECRET_KEY` via variável de ambiente
- `ALLOWED_HOSTS` configurado

### Banco de Dados
- Suporte a PostgreSQL via `dj-database-url`
- Fallback para SQLite em desenvolvimento

### Arquivos Estáticos
- `WhiteNoise` para servir arquivos estáticos
- `STATIC_ROOT` configurado
- Compressão automática de arquivos

### Servidor Web
- `Gunicorn` como servidor WSGI
- Configuração otimizada para produção

## Comandos Executados no Deploy

1. `python manage.py migrate` - Aplica migrações do banco
2. `python manage.py collectstatic --noinput` - Coleta arquivos estáticos
3. `gunicorn client_dashboard.wsgi:application` - Inicia o servidor

## Monitoramento

Após o deploy, você pode:
- Ver logs em tempo real no painel do Railway
- Configurar domínio customizado
- Monitorar métricas de performance

## Troubleshooting

### Erro de Migração
Se houver erro nas migrações, execute no Railway CLI:
```bash
railway run python client_dashboard/manage.py migrate
```

### Arquivos Estáticos não Carregam
Verifique se `STATIC_ROOT` está configurado e execute:
```bash
railway run python client_dashboard/manage.py collectstatic
```

### Erro de Conexão com Banco
Verifique se a variável `DATABASE_URL` está configurada no painel do Railway.

## Próximos Passos

1. Configure um domínio customizado
2. Configure SSL (automático no Railway)
3. Configure backup do banco de dados
4. Monitore logs e performance