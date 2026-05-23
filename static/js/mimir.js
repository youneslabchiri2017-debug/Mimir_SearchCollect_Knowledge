user_promp_action = document.getElementById("user-input")

async function sendMessage() {
    term = user_promp_action.value
    request = await fetch(`api/terms/${term}`)
    response = await request.json()
    console.log(response)
}