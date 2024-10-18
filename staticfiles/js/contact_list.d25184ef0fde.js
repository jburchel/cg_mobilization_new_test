document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const contactsBody = document.getElementById('contacts-body');
    const searchResultsCount = document.getElementById('search-results-count');
    const contactRows = document.querySelectorAll('.contact-row');

    function filterContacts(searchTerm) {
        let visibleCount = 0;
        contactRows.forEach(row => {
            const contactData = row.textContent.toLowerCase();
            if (contactData.includes(searchTerm.toLowerCase())) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        searchResultsCount.textContent = `${visibleCount} contact(s) found`;
    }

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterContacts(this.value);
        });

        // Initial count
        searchResultsCount.textContent = `${contactRows.length} contact(s) found`;
    } else {
        console.error('Search input element not found');
    }
});
