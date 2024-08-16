// Get the first dropdown field
var contactTypeField = document.getElementById('id_contact_type');

// Get the second dropdown field
var contactField = document.getElementById('id_contact');

// Define a function to update the options in the second dropdown field
function updateContactField() {
    var contactType = contactTypeField.value;
    if (contactType == 'church') {
        // Use an AJAX request to get the list of churches from the server
        $.ajax({
            type: 'GET',
            url: '/static/churches/', // URL of the view that returns the list of churches
            dataType: 'json',
            success: function(data) {
                // Update the options in the second dropdown field
                contactField.innerHTML = '';
                for (var i = 0; i < data.length; i++) {
                    var option = document.createElement('option');
                    option.value = data[i].id;
                    option.text = data[i].name;
                    contactField.appendChild(option);
                }
            }
        });
    } else if (contactType == 'people') {
        // Use an AJAX request to get the list of people from the server
        $.ajax({
            type: 'GET',
            url: '/static/people/', // URL of the view that returns the list of people
            dataType: 'json',
            success: function(data) {
                // Update the options in the second dropdown field
                contactField.innerHTML = '';
                for (var i = 0; i < data.length; i++) {
                    var option = document.createElement('option');
                    option.value = data[i].id;
                    option.text = data[i].name;
                    contactField.appendChild(option);
                }
            }
        });
    }
}

// Call the updateContactField function when the value of the first dropdown field changes
contactTypeField.addEventListener('change', updateContactField);

// Call the updateContactField function when the page loads
updateContactField();