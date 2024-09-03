$(document).ready(function() {
    $('#id_contact').select2({
        placeholder: "Select a contact",
        allowClear: true,
        templateResult: formatContact,
        templateSelection: formatContact
    });
});

function formatContact(contact) {
    if (!contact.id) {
        return contact.text;
    }
    var $contact = $(
        '<span>' + contact.text.split(' (')[0] + ' <small style="color: #999;">' + contact.text.split(' (')[1].replace(')', '') + '</small></span>'
    );
    return $contact;
}