user_promp_action = document.getElementById("user-input")
chat = document.getElementById("chat-messages")

async function sendMessage() {
    term = user_promp_action.value
    request = await fetch(`api/terms/${term}`)
    response = await request.json()
    chat.innerHTML += `<div class="user-message">${term}</div>`
    chat.innerHTML += `<div class="message ai-message">${response}</div>`
}