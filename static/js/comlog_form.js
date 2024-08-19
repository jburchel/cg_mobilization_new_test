$(document).ready(function() {
    console.log("ComLog form script loaded");

    var contactField = $('#id_contact');
    var contactIdField = $('#id_contact_id');
    var contactTypeField = $('#id_contact_type');

    console.log("Contact field:", contactField.length);
    console.log("Contact ID field:", contactIdField.length);
    console.log("Contact Type field:", contactTypeField.length);

    contactTypeField.on('change', function() {
        console.log("Contact type changed:", $(this).val());
        contactField.val('');
        contactIdField.val('');
    });

    contactField.autocomplete({
        source: function(request, response) {
            console.log("Autocomplete request:", request.term);
            $.ajax({
                url: contactSearchUrl,
                dataType: "json",
                data: {
                    term: request.term,
                    type: contactTypeField.val()
                },
                success: function(data) {
                    console.log("Autocomplete response:", data);
                    response(data);
                },
                error: function(xhr, status, error) {
                    console.error("Autocomplete error:", status, error);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            console.log("Item selected:", ui.item);
            contactField.val(ui.item.value);
            contactIdField.val(ui.item.id);
            return false;
        },
        open: function() {
            console.log("Autocomplete dropdown opened");
        }
    });

    console.log("Autocomplete initialized");
});