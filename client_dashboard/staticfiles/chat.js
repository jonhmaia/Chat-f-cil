document.addEventListener('DOMContentLoaded', () => {
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