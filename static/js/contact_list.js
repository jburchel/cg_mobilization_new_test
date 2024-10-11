document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const contactsBody = document.getElementById('contacts-body');
    const searchResultsCount = document.getElementById('search-results-count');

    function renderContacts(contacts) {
        contactsBody.innerHTML = '';
        if (contacts.length === 0) {
            contactsBody.innerHTML = '<tr><td colspan="6">No contacts found.</td></tr>';
        } else {
            contacts.forEach(contact => {
                const row = document.createElement('tr');
                row.className = 'contact-row';
                row.innerHTML = `
                    <td data-label="Name">${contact.name}</td>
                    <td data-label="Email">${contact.email}</td>
                    <td data-label="Phone">${contact.phone}</td>
                    <td data-label="Last Contact">${contact.date_modified}</td>
                    <td data-label="Actions">
                        <a href="/contacts/edit/${contact.id}/" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                `;
                contactsBody.appendChild(row);
            });
        }
        searchResultsCount.textContent = `${contacts.length} contact(s) found`;
    }

    function filterContacts(searchTerm) {
        const filtered = contactsData.filter(contact => {
            const searchFields = [
                contact.name,
                contact.email,
                contact.phone,
                contact.date_modified
            ];
            return searchFields.some(field => 
                field && field.toLowerCase().includes(searchTerm.toLowerCase())
            );
        });
        renderContacts(filtered);
    }

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterContacts(this.value);
        });

        // Initial render of all contacts
        renderContacts(contactsData);
    } else {
        console.error('Search input element not found');
    }
});