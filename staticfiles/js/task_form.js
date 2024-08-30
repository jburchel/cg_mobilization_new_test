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
});