document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('contact-search');
    const contactsBody = document.getElementById('contacts-body');
    const noResults = document.getElementById('no-results');

    function renderContacts(contacts) {
        contactsBody.innerHTML = '';
        if (contacts.length === 0) {
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
            contacts.forEach(contact => {
                const detailUrl = contact.type === 'Church' ? `/contacts/church/${contact.id}/` : `/contacts/person/${contact.id}/`;
                const editUrl = contact.type === 'Church' ? `/contacts/church/${contact.id}/edit/` : `/contacts/person/${contact.id}/edit/`;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><a href="${detailUrl}">${contact.name}</a></td>
                    <td>${contact.type}</td>
                    <td>${contact.email}</td>
                    <td>${contact.phone}</td>
                    <td>${contact.last_contact}</td>
                    <td class="actions">
                        <a href="${editUrl}" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                `;
                contactsBody.appendChild(row);
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

        // Initial render of all contacts
        if (typeof contactsData !== 'undefined' && Array.isArray(contactsData)) {
            renderContacts(contactsData);
        } else {
            console.error('contactsData is not defined or is not an array');
            noResults.style.display = 'block';
        }
    }

    // Add touch-to-scroll hint for mobile devices
    if ('ontouchstart' in window) {
        const tableResponsive = document.querySelector('.table-responsive');
        if (tableResponsive) {
            const scrollHint = document.createElement('div');
            scrollHint.className = 'scroll-hint';
            scrollHint.textContent = 'Swipe to see more';
            tableResponsive.appendChild(scrollHint);

            tableResponsive.addEventListener('scroll', function() {
                scrollHint.style.opacity = '0';
                setTimeout(() => {
                    scrollHint.remove();
                }, 300);
            }, { once: true });
        }
    }
});