// edit_contact.js

document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle spouse fields based on marital status
    function toggleSpouseFields() {
        const maritalStatus = document.getElementById('id_marital_status');
        const spouseFields = document.querySelectorAll('[id^="id_spouse_"]');

        if (maritalStatus) {
            maritalStatus.addEventListener('change', function() {
                const showSpouseFields = this.value === 'married' || this.value === 'engaged';
                spouseFields.forEach(field => {
                    field.closest('.form-group').style.display = showSpouseFields ? 'block' : 'none';
                });
            });

            // Trigger the change event on page load
            maritalStatus.dispatchEvent(new Event('change'));
        }
    }

    // Call the function to set up the toggle behavior
    toggleSpouseFields();
});