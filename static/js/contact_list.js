document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const contactsBody = document.getElementById('contacts-body');
    const cardView = document.querySelector('.card-view');
    const noResults = document.getElementById('no-results');
    const tableView = document.querySelector('.table-view');

    function renderContacts(contacts) {
        contactsBody.innerHTML = '';
        cardView.innerHTML = '';
        if (contacts.length === 0) {
            noResults.style.display = 'block';
            tableView.style.display = 'none';
            cardView.style.display = 'none';
        } else {
            noResults.style.display = 'none';
            tableView.style.display = 'block';
            cardView.style.display = 'block';
            contacts.forEach(contact => {
                // Table row
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><a href="${contact.detail_url}">${contact.name}</a></td>
                    <td>${contact.type}</td>
                    <td class="hide-mobile">${contact.email}</td>
                    <td class="hide-mobile">${contact.phone}</td>
                    <td class="hide-mobile">${contact.last_contact}</td>
                    <td class="actions">
                        <a href="${contact.edit_url}" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                `;
                contactsBody.appendChild(row);

                // Card
                const card = document.createElement('div');
                card.className = 'contact-card';
                card.innerHTML = `
                    <h3><a href="${contact.detail_url}">${contact.name}</a></h3>
                    <p>Type: ${contact.type}</p>
                    <p>Email: ${contact.email}</p>
                    <p>Phone: ${contact.phone}</p>
                    <p>Last Contact: ${contact.last_contact}</p>
                    <a href="${contact.edit_url}" class="btn btn-sm btn-warning">Edit</a>
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

        // Initial render
        renderContacts(contactsData);
    }
});