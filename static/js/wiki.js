const searchInput = document.getElementById('search-input');
const dropdown = document.getElementById('search-dropdown');
let debounceTimer;

searchInput.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    
    clearTimeout(debounceTimer);

    // Si escribe menos de 2 caracteres, ocultamos el panel
    if (query.length < 2) {
        dropdown.style.display = 'none';
        return;
    }

    debounceTimer = setTimeout(async () => {try {
        // Consultamos nuestro nuevo endpoint asíncrono del backend
        const response = await fetch(`/api/terms/search_qid?term=${encodeURIComponent(query)}`);
        const items = await response.json();

        if (items.length === 0) {
            dropdown.style.display = 'none';
            return;
        }

        // Limpiamos resultados anteriores e inyectamos los nuevos
        dropdown.innerHTML = '';
        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'dropdown-item';
            row.innerHTML = `<span>🎯</span> <span class="qid-badge">${item}</span>`;
            
            // Al hacer click, redirige directamente a la wiki de ese QID
            row.addEventListener('click', () => {
                window.location.href = `/mimir_wiki/${item}`;
            });
            dropdown.appendChild(row);
        });

        dropdown.style.display = 'block';
    } catch (err) {
        console.error("Error obteniendo runas de búsqueda:", err);
    }
    }, 300)
    });

// Cerrar el menú si el usuario hace click fuera del buscador
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});