document.addEventListener('DOMContentLoaded', function() {
    var reminderSelect = document.getElementById('id_reminder');
    var customReminderGroup = document.getElementById('custom-reminder-group');


    function toggleCustomReminder() {
        if (reminderSelect.value === 'custom') {
            customReminderGroup.style.display = 'block';
        } else {
            customReminderGroup.style.display = 'none';
        }
    }

    reminderSelect.addEventListener('change', toggleCustomReminder);
    toggleCustomReminder(); // Call once to set initial state

    var dueDateInput = document.getElementById('id_due_date');
    
    if (dueDateInput) {
        dueDateInput.addEventListener('change', function() {
            var value = this.value;
            if (value && !value.includes('T')) {
                // If the value doesn't include 'T', it's likely in an incompatible format
                var date = new Date(value);
                var isoString = date.toISOString();
                this.value = isoString.slice(0, 16);  // Keep only YYYY-MM-DDTHH:MM
            }
        });
    }
});