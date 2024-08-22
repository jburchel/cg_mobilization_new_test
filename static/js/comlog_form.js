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
                    response($.map(data, function(item) {
                        return {
                            label: item.label,
                            value: item.value,
                            id: item.id
                        };
                    }));
                },
                error: function(xhr, status, error) {
                    console.error("Autocomplete error:", status, error);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            console.log("Item selected:", ui.item);
            contactField.val(ui.item.label);
            contactIdField.val(ui.item.id);
            return false;
        },
        focus: function(event, ui) {
            contactField.val(ui.item.label);
            return false;
        }
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append("<div>" + item.label + "</div>")
            .appendTo(ul);
    };

    console.log("Autocomplete initialized");
});