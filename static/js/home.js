const term = document.getElementById('portal-q');
const deep_s = document.getElementById('portal-deep-search');

async function invokePortal(){
    let term_value = term.value.trim()
    let deep_value = deep_s.checked

    console.log(term_value, deep_value)

    let form_data = new FormData()
    form_data.append('q', term_value)
    form_data.append('deep', deep_value)

    try{
        let req = await fetch('api/terms/', {
                    method: 'POST', 
                    body: form_data
                })
        let res = await req.json()
        if (res.status == 'success') {
            window.location.href = '/terms/' + res.term_id
        }else {
            alert('Error: ' + res.message)
        }
    }catch (error) {
        alert('Error: ' + error.message)
    }
}
    