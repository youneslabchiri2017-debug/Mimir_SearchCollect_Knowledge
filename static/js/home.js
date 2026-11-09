async function invokePortal() {
    const queryInput = document.getElementById('portal-q');
    const deepCheckbox = document.getElementById('portal-deep-search');
    const query = queryInput.value.trim();
    const deep = deepCheckbox ? deepCheckbox.checked : false;

    if (!query) {
        alert("Por favor, introduce un término para invocar conocimiento.");
        return;
    }

    // Contenedor o elemento para mostrar el feedback visual al usuario
    let feedbackContainer = document.getElementById('portal-feedback');
    if (!feedbackContainer) {
        feedbackContainer = document.createElement('div');
        feedbackContainer.id = 'portal-feedback';
        feedbackContainer.style.marginTop = '15px';
        feedbackContainer.style.padding = '12px';
        feedbackContainer.style.borderRadius = '6px';
        feedbackContainer.style.backgroundColor = 'var(--bg-input, #334155)';
        feedbackContainer.style.color = 'var(--primary-color, #38bdf8)';
        feedbackContainer.style.fontFamily = 'monospace';
        feedbackContainer.style.fontSize = '0.9rem';
        
        const portalForm = document.querySelector('.portal-form');
        portalForm.appendChild(feedbackContainer);
    }

    feedbackContainer.innerHTML = "🌀 Abriendo portales hacia GraphDB y los Nueve Mundos...";

    try {
        const response = await fetch('/api/terms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ q: query, deep: deep })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.message || `Error del servidor (${response.status})`);
        }

        feedbackContainer.innerHTML = "✨ ¡Conocimiento invocado con éxito! Redirigiendo a la Wiki...";
        const result = await response.json();

        if (result.term_id) {
            setTimeout(() => {
                window.location.href = `/mimir_wiki/${result.term_id}`;
            }, 1000);
        } else {
            throw new Error("No se ha devuelto un identificador válido (QID).");
        }

    } catch (err) {
        console.error("Error en la invocación:", err);
        feedbackContainer.innerHTML = `❌ Error: ${err.message}`;
        feedbackContainer.style.color = '#ef4444'; // Color rojo de error
    }
}