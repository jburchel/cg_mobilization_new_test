document.addEventListener('DOMContentLoaded', function() {
    const contactTypeSelect = document.getElementById('id_contact_type');
    const contactInput = document.getElementById('id_contact');
    const contactIdInput = document.getElementById('id_contact_id');

    function loadContacts() {
        const contactType = contactTypeSelect.value;
        fetch(`/api/contacts/?type=${contactType}`)
            .then(response => response.json())
            .then(data => {
                const datalist = document.getElementById('contacts-list');
                datalist.innerHTML = '';
                data.forEach(contact => {
                    const option = document.createElement('option');
                    option.value = contact.name;
                    option.dataset.id = contact.id;
                    datalist.appendChild(option);
                });
            });
    }

    contactTypeSelect.addEventListener('change', loadContacts);

    contactInput.addEventListener('input', function() {
        const selectedOption = Array.from(document.getElementById('contacts-list').options)
            .find(option => option.value === contactInput.value);
        if (selectedOption) {
            contactIdInput.value = selectedOption.dataset.id;
        }
    });

    // Load contacts on page load if editing
    if (contactTypeSelect.value) {
        loadContacts();
    }
});