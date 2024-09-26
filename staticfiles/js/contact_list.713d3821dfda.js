document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const contactsBody = document.getElementById('contacts-body');

    function renderContacts(contacts) {
        contactsBody.innerHTML = '';
        if (contacts.length === 0) {
            contactsBody.innerHTML = '<tr><td colspan="6">No contacts found.</td></tr>';
        } else {
            contacts.forEach(contact => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td data-label="Name">
                        <a href="${contact.detail_url}">
                            ${contact.name} (${contact.type})
                        </a>
                    </td>
                    <td data-label="Type">${contact.type}</td>
                    <td data-label="Email">${contact.email}</td>
                    <td data-label="Phone">${contact.phone}</td>
                    <td data-label="Last Contact">${contact.last_contact}</td>
                    <td data-label="Actions">
                        <a href="${contact.edit_url}" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                `;
                contactsBody.appendChild(row);
            });
        }
    }

    function filterContacts(searchTerm) {
        const filtered = contactsData.filter(contact => {
            const searchFields = [
                contact.name,
                contact.email,
                contact.type,
                contact.source,
                contact.title
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
    }
});