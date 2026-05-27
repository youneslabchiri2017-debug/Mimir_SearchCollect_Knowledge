const mainContainer = document.getElementById('main-container');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const skeletonLoader = document.getElementById('skeleton-loader');
const resultCard = document.getElementById('result-card');
const resultTitle = document.getElementById('result-title');
const resultText = document.getElementById('result-text');

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        executeSearch();
    }
}

async function executeSearch() {
    let new_term = searchInput.value
    if (!new_term) {
        alert('Please enter a search term.');
        return;
    }
    request = await fetch(`api/terms/${new_term}`, {
        method: 'POST',
        })
    response = await request.json()
    console.log(response)
}