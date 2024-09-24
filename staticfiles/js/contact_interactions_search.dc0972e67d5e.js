document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const interactions = document.querySelectorAll('.interaction');
    const noResultsMessage = document.createElement('tr');
    noResultsMessage.innerHTML = '<td colspan="4">No interactions found.</td>';
    noResultsMessage.classList.add('no-results');

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        let hasResults = false;

        interactions.forEach(function(interaction) {
            const content = interaction.getAttribute('data-content').toLowerCase();
            if (content.includes(searchTerm)) {
                interaction.style.display = '';
                hasResults = true;
            } else {
                interaction.style.display = 'none';
            }
        });

        if (!hasResults) {
            document.querySelector('tbody').appendChild(noResultsMessage);
        } else {
            noResultsMessage.remove();
        }
    }

    searchInput.addEventListener('input', performSearch);

    // Add touch support for mobile devices
    searchInput.addEventListener('touchstart', function() {
        this.focus();
    });

    // Initial search to handle any pre-filled value
    performSearch();
});