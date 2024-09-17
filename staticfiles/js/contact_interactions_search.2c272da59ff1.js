document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const interactions = document.querySelectorAll('.interaction');

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();

        interactions.forEach(function(interaction) {
            const content = interaction.getAttribute('data-content');
            if (content.includes(searchTerm)) {
                interaction.classList.remove('hidden');
            } else {
                interaction.classList.add('hidden');
            }
        });
    });
});
