document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const contactsBody = document.getElementById('contacts-body');
    const cardView = document.querySelector('.card-view');
    const noResults = document.getElementById('no-results');

    function renderContacts(contacts) {
        contactsBody.innerHTML = '';
        cardView.innerHTML = '';
        if (contacts.length === 0) {
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
            contacts.forEach(contact => {
                const detailUrl = contact.type === 'Church' ? `/contacts/church/${contact.id}/` : `/contacts/person/${contact.id}/`;
                const editUrl = contact.type === 'Church' ? `/contacts/church/${contact.id}/edit/` : `/contacts/person/${contact.id}/edit/`;
                
                // Table row
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><a href="${detailUrl}">${contact.name}</a></td>
                    <td>${contact.type}</td>
                    <td class="hide-mobile">${contact.email}</td>
                    <td class="hide-mobile">${contact.phone}</td>
                    <td class="hide-mobile">${contact.last_contact}</td>
                    <td class="actions">
                        <a href="${editUrl}" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                `;
                contactsBody.appendChild(row);

                // Card
                const card = document.createElement('div');
                card.className = 'contact-card';
                card.innerHTML = `
                    <h3><a href="${detailUrl}">${contact.name}</a></h3>
                    <p>Type: ${contact.type}</p>
                    <p>Email: ${contact.email}</p>
                    <p>Phone: ${contact.phone}</p>
                    <p>Last Contact: ${contact.last_contact}</p>
                    <a href="${editUrl}" class="btn btn-sm btn-warning">Edit</a>
                `;
                cardView.appendChild(card);
            });
        }
    }

    function filterContacts(searchTerm) {
        if (!searchTerm) {
            renderContacts(contactsData);
            return;
        }

        const filtered = contactsData.filter(contact => {
            const searchFields = [
                contact.name,
                contact.type,
                contact.email,
                contact.phone,
                contact.last_contact,
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

        if (typeof contactsData !== 'undefined' && Array.isArray(contactsData)) {
            renderContacts(contactsData);
        } else {
            console.error('contactsData is not defined or is not an array');
            noResults.style.display = 'block';
        }
    }
});