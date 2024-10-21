document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const pipelineFilter = document.getElementById('pipeline-filter');
    const contactsBody = document.getElementById('contacts-body');
    const searchResultsCount = document.getElementById('search-results-count');
    const contactRows = document.querySelectorAll('.contact-row');

    function filterContacts() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedPipeline = pipelineFilter.value;
        let visibleCount = 0;

        contactRows.forEach(row => {
            const contactData = row.textContent.toLowerCase();
            const churchPipeline = row.dataset.churchPipeline;
            const peoplePipeline = row.dataset.peoplePipeline;
            
            const matchesSearch = contactData.includes(searchTerm);
            const matchesPipeline = selectedPipeline === '' || 
                                    `church_${churchPipeline}` === selectedPipeline ||
                                    `people_${peoplePipeline}` === selectedPipeline;

            if (matchesSearch && matchesPipeline) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        searchResultsCount.textContent = `${visibleCount} contact(s) found`;
    }

    if (searchInput && pipelineFilter) {
        searchInput.addEventListener('input', filterContacts);
        pipelineFilter.addEventListener('change', filterContacts);

        // Initial count
        searchResultsCount.textContent = `${contactRows.length} contact(s) found`;
    }
});
