document.addEventListener('DOMContentLoaded', () => {
    // Injetar CSS diretamente no documento
    const style = document.createElement('style');
    style.textContent = `
        :root {
            --primary-color: #007bff;
            --chat-background: #ffffff;
            --font-family: Arial, sans-serif;
            --bot-message-bg: #f1f1f1;
            --user-message-bg: #e1f5fe;
        }

        #chat-bubble {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: var(--primary-color);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 9998;
        }

        #chat-bubble svg {
            width: 32px;
            height: 32px;
            fill: white;
        }

        #chat-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background-color: var(--chat-background);
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
            flex-direction: column;
            z-index: 9999;
        }

        #chat-window.active {
            display: flex;
        }

        .chat-header {
            background-color: var(--primary-color);
            color: white;
            padding: 15px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            text-align: center;
            font-weight: bold;
        }

        .chat-messages {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .message {
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 80%;
            line-height: 1.4;
        }

        .message.bot {
            background-color: var(--bot-message-bg);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        .message.user {
            background-color: var(--user-message-bg);
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .chat-input-form {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
        }

        #chat-input {
            flex-grow: 1;
            border: 1px solid #ccc;
            border-radius: 20px;
            padding: 10px 15px;
            outline: none;
            font-size: 1rem;
        }

        #chat-input:focus {
            border-color: var(--primary-color);
        }

        #send-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 10px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        #send-btn svg {
            width: 20px;
            height: 20px;
            fill: white;
        }
    `;
    document.head.appendChild(style);

    const scriptTag = document.querySelector('script[data-chatbot-id]');
    const chatbotId = scriptTag.dataset.chatbotId;
    const welcomeMessage = scriptTag.dataset.welcomeMessage || 'Olá! Como posso ajudar?';

    if (!chatbotId) {
        console.error('Chatbot ID não encontrado na tag do script.');
        return;
    }

    const chatContainer = document.createElement('div');
    chatContainer.id = 'chat-container';
    document.body.appendChild(chatContainer);

    const chatIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>`;
    const sendIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>`;

    // Estrutura HTML do chat
    chatContainer.innerHTML = `
        <div id="chat-bubble">${chatIcon}</div>
        <div id="chat-window">
            <div class="chat-header">Assistente Virtual</div>
            <div class="chat-messages">
                <div class="message bot">${welcomeMessage}</div>
            </div>
            <form class="chat-input-form">
                <input type="text" id="chat-input" placeholder="Digite sua mensagem..." autocomplete="off">
                <button type="submit" id="send-btn">${sendIcon}</button>
            </form>
        </div>
    `;

    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const chatMessages = document.querySelector('.chat-messages');
    const chatInputForm = document.querySelector('.chat-input-form');
    const chatInput = document.getElementById('chat-input');
    
    // Ponto 3: Eventos
    chatBubble.addEventListener('click', () => {
        chatWindow.classList.toggle('active');
        if (chatWindow.classList.contains('active')) {
            chatInput.focus();
        }
    });

    chatInputForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const messageText = chatInput.value.trim();
        if (messageText) {
            sendMessage(messageText);
        }
    });

    // Ponto 4: Função de Envio
    function addMessage(text, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
    }

    async function sendMessage(userMessage) {
        // Exibir a mensagem do usuário imediatamente
        addMessage(userMessage, 'user');
        const messageToSend = userMessage;
        chatInput.value = '';

        try {
            // Fazer a requisição fetch para o backend proxy usando a nova API
            const response = await fetch('/api/v1/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    chatbot_id: chatbotId,
                    message: messageToSend,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Exibir a resposta da IA - verificar diferentes formatos de resposta
            let aiReply;
            if (data.reply) {
                aiReply = data.reply;
            } else if (data.mensagem) {
                aiReply = data.mensagem;
            } else if (data.message) {
                aiReply = data.message;
            } else if (data.response) {
                aiReply = data.response;
            } else {
                aiReply = 'Não recebi uma resposta válida.';
            }
            
            addMessage(aiReply, 'bot');

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            addMessage('Desculpe, não consegui me conectar ao servidor.', 'bot');
        }
    }
});