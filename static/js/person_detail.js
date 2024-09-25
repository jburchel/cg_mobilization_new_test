document.addEventListener('DOMContentLoaded', function() {
    const phoneDropdowns = document.querySelectorAll('.phone-dropdown');

    phoneDropdowns.forEach(dropdown => {
        const phoneLink = dropdown.querySelector('.phone-link');
        const dropdownContent = dropdown.querySelector('.dropdown-content');

        phoneLink.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            dropdownContent.classList.toggle('show');
        });

        const phoneOptions = dropdown.querySelectorAll('.phone-option');
        phoneOptions.forEach(option => {
            option.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
                const action = this.getAttribute('data-action');
                const personId = phoneLink.getAttribute('person-id');
                const phoneNumber = phoneLink.getAttribute('data-phone');
                handleCommunication(action, personId, phoneNumber);
                dropdownContent.classList.remove('show');
            });
        });

        // Close the dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!dropdown.contains(event.target)) {
                dropdownContent.classList.remove('show');
            }
        });
    });
});

function handleCommunication(action, personId, phoneNumber) {
    let communicationType = action === 'phone' ? 'phone' : 'text';
    let notes = `${action.charAt(0).toUpperCase() + action.slice(1)} communication initiated to ${phoneNumber}`;

    // Create the com log entry
    fetch('/com_log/api/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            person_id: personId,
            communication_type: communicationType,
            notes: notes
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Com log entry created:', data);
        // Proceed with the phone call or text message
        if (action === 'phone') {
            window.location.href = `tel:${phoneNumber}`;
        } else {
            window.location.href = `sms:${phoneNumber}`;
        }
    })
    .catch(error => {
        console.error('Error creating com log entry:', error);
        // Proceed with the phone call or text message even if the com log entry creation fails
        if (action === 'phone') {
            window.location.href = `tel:${phoneNumber}`;
        } else {
            window.location.href = `sms:${phoneNumber}`;
        }
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}