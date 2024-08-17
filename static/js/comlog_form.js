document.addEventListener('DOMContentLoaded', function() {
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
                contactSearchResults.innerHTML = '';
                if (data.length === 0) {
                    const div = document.createElement('div');
                    div.textContent = 'No results found';
                    contactSearchResults.appendChild(div);
                } else {
                    data.forEach(contact => {
                        const div = document.createElement('div');
                        div.textContent = contact.name;
                        div.addEventListener('click', function() {
                            contactInput.value = contact.name;
                            contactSearchResults.innerHTML = '';
                        });
                        contactSearchResults.appendChild(div);
                    });
                }
                // Make sure the results are visible
                contactSearchResults.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                contactSearchResults.innerHTML = `<div>Error: ${error.message}</div>`;
                contactSearchResults.style.display = 'block';
            });
    }

    // Close search results when clicking outside
    document.addEventListener('click', function(event) {
        if (!contactInput.contains(event.target) && !contactSearchResults.contains(event.target)) {
            contactSearchResults.style.display = 'none';
            console.log('Dropdown hidden (clicked outside)');
        }
    });

    console.log('Event listeners set up.');
});