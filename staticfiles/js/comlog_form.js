document.addEventListener('DOMContentLoaded', function() {
    alert('ComLog form script loaded');
    const contactTypeSelect = document.getElementById('id_contact_type');
    const contactInput = document.getElementById('id_contact');
    const contactSearchResults = document.createElement('div');
    contactSearchResults.className = 'contact-search-results';
    contactInput.parentNode.insertBefore(contactSearchResults, contactInput.nextSibling);

    let debounceTimer;

    console.log('Script loaded. Setting up event listeners.');

    contactTypeSelect.addEventListener('change', function() {
        console.log('Contact type changed:', this.value);
        contactInput.value = '';
        contactSearchResults.innerHTML = '';
    });

    contactInput.addEventListener('input', function() {
        console.log('Input changed:', this.value);
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(searchContacts, 300);
    });

    function searchContacts() {
        const searchTerm = contactInput.value;
        const contactType = contactTypeSelect.value;

        console.log('Searching for:', searchTerm, 'Type:', contactType);

        if (searchTerm.length < 2) {
            contactSearchResults.innerHTML = '';
            return;
        }

        const url = `/contacts/api/search/?type=${contactType}&term=${encodeURIComponent(searchTerm)}`;
        console.log('Fetching from:', url);

        fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                // ... rest of your code to handle the results ...
            })
            .catch(error => console.error('Error:', error));
    }

    // Close search results when clicking outside
    document.addEventListener('click', function(event) {
        if (!contactInput.contains(event.target) && !contactSearchResults.contains(event.target)) {
            contactSearchResults.innerHTML = '';
            console.log('Dropdown hidden (clicked outside)');
        }
    });

    console.log('Event listeners set up.');
});