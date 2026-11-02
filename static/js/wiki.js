// --- 1. BUSCADOR DINÁMICO & EVENTOS DE NAVEGACIÓN ---
const searchInput = document.getElementById('search-input');
const dropdown = document.getElementById('search-dropdown');
let debounceTimer;

if (searchInput) {
    searchInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            if (dropdown) dropdown.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/api/terms/search_qid?term=${encodeURIComponent(query)}`);
                const items = await response.json();

                if (!dropdown) return;

                if (items.length === 0) {
                    dropdown.style.display = 'none';
                    return;
                }

                dropdown.innerHTML = '';
                items.forEach(item => {
                    const row = document.createElement('div');
                    row.className = 'dropdown-item';
                    row.style.padding = '8px 12px';
                    row.style.cursor = 'pointer';
                    row.style.borderBottom = '1px solid var(--border-color)';
                    row.innerHTML = `<span>🎯</span> <span class="qid-badge" style="color: var(--primary-color);">${item}</span>`;

                    row.addEventListener('click', () => {
                        window.location.href = `/mimir_wiki/${item}`;
                    });
                    dropdown.appendChild(row);
                });

                dropdown.style.display = 'block';
            } catch (err) {
                console.error("Error obteniendo runas de búsqueda:", err);
            }
        }, 300);
    });
}

// Cerrar el menú desplegable si el usuario hace click fuera
document.addEventListener('click', (e) => {
    if (searchInput && dropdown && !searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});

// DESCARGA DE ARCHIVOS RDF
async function download_rdf(uri, name) {
    let link = document.createElement("a");
    link.download = name;
    link.href = uri;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// --- 2. INICIALIZACIÓN DE GRÁFICOS (GRAPHDB / PROVENANCE) ---
document.addEventListener('DOMContentLoaded', () => {
    // Si no existen datos pasados por el template, tomamos valores por defecto
    const graphData = window.MIMIR_GRAPH_DATA || {
        origenes: ['Wikidata (http://wikidata.org)', 'DBpedia (http://dbpedia.org)', 'Mimir Internal (http://mimir.org/prov)'],
        cantidades: [42, 25, 15],
        interseccionLabels: ['Exclusivo Wikidata', 'Exclusivo DBpedia', 'Intersección (Compartidos)'],
        interseccionValores: [30, 15, 37]
    };

    // Estilos comunes para Chart.js respetando wiki.css
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

    // A) Gráfico de Barras: Tripletas por Lugar de Origen / Named Graph
    const barCtx = document.getElementById('barChartOrigins');
    if (barCtx) {
        new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: graphData.origenes,
                datasets: [{
                    label: 'Cantidad de Tripletas',
                    data: graphData.cantidades,
                    backgroundColor: 'rgba(56, 189, 248, 0.6)',
                    borderColor: '#38bdf8',
                    borderWidth: 1.5,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(51, 65, 85, 0.5)' }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(51, 65, 85, 0.5)' }
                    }
                }
            }
        });
    }

    // B) Gráfico de Sectores / Donut: Intersección y Composición del Subgrafo
    const donutCtx = document.getElementById('donutChartIntersection');
    if (donutCtx) {
        new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: graphData.interseccionLabels,
                datasets: [{
                    data: graphData.interseccionValores,
                    backgroundColor: [
                        '#38bdf8', // Blue Cyan
                        '#10a37f', // Mimir Green
                        '#f59e0b', // Amber/Yellow
                        '#8b5cf6'  // Purple
                    ],
                    borderWidth: 2,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15 }
                    }
                },
                cutout: '65%'
            }
        });
    }
});