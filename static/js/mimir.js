const user_promp_action = document.getElementById("user-input");
const chat = document.getElementById("chat-messages");

function sendMessage() {
    const prompt = user_promp_action.value.trim();
    if (!prompt) return;

    user_promp_action.value = "";

    // 1. Añadimos el mensaje del usuario al chat
    chat.innerHTML += `<div class="user-message">${prompt}</div>`;

    // 2. Creamos una única burbuja para Mimir que mostrará los estados y luego la respuesta
    const aiMessageDiv = document.createElement("div");
    aiMessageDiv.className = "message ai-message";
    aiMessageDiv.innerHTML = `<span class="mimir-loading" style="color: #10a37f; font-style: italic;">Mimir está escuchando...</span>`;
    chat.appendChild(aiMessageDiv);
    
    // Auto-scroll hacia abajo
    chat.scrollTop = chat.scrollHeight;

    // 3. Abrimos el canal de Server-Sent Events (SSE)
    // Usamos encodeURIComponent para proteger caracteres especiales en la URL
    const eventSource = new EventSource(`api/ask_mimir/${encodeURIComponent(prompt)}`);

    // Escuchamos las actualizaciones del servidor
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.status) {
            // Si el servidor envía un estado, lo mostramos dinámicamente
            aiMessageDiv.innerHTML = `<span class="mimir-loading" style="color: #10a37f; font-style: italic;">${data.status}</span>`;
        } 
        
        if (data.response) {
            // Cuando llega la respuesta final, la inyectamos y cerramos el canal
            aiMessageDiv.innerHTML = data.response;
            eventSource.close();
        }

        if (data.error) {
            // Si ocurre un error controlado en el servidor
            aiMessageDiv.innerHTML = `<span style="color: #ff4a4a;">Mimir: ${data.error}</span>`;
            eventSource.close();
        }

        chat.scrollTop = chat.scrollHeight;
    };

    // En caso de que se caiga la conexión de red de imprevisto
    eventSource.onerror = function(err) {
        console.error("Error en el enlace SSE:", err);
        aiMessageDiv.innerHTML = `<span style="color: #ff4a4a;">Mimir: Se ha cortado el enlace rúnico con el servidor.</span>`;
        eventSource.close();
    };
}