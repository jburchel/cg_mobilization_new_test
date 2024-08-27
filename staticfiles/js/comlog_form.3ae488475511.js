document.addEventListener('DOMContentLoaded', function() {
    const contactTypeSelect = document.getElementById('id_contact_type');
    const contactInput = document.getElementById('id_contact');
    const contactIdInput = document.getElementById('id_contact_id');

    function initializeAutocomplete() {
        $(contactInput).autocomplete({
            source: function(request, response) {
                const contactType = contactTypeSelect.value;
                $.ajax({
                    url: "/com_log/contact-search/",
                    dataType: "json",
                    data: {
                        term: request.term,
                        type: contactType
                    },
                    success: function(data) {
                        response(data);
                    }
                });
            },
            minLength: 2,
            select: function(event, ui) {
                contactIdInput.value = ui.item.id;
            }
        });
    }

    contactTypeSelect.addEventListener('change', function() {
        contactInput.value = '';
        contactIdInput.value = '';
        initializeAutocomplete();
    });

    // Initialize autocomplete on page load
    initializeAutocomplete();
});