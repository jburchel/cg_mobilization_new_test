function handlePhoneClick(event, personId, phoneNumber) {
    event.preventDefault();

    // Create the com log entry
    fetch('/com_log/api/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            person_id: personId,
            communication_type: 'phone',
            notes: `Phone call initiated to ${phoneNumber}`
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Com log entry created:', data);
        // Proceed with the phone call
        window.location.href = `tel:${phoneNumber}`;
    })
    .catch(error => {
        console.error('Error creating com log entry:', error);
        // Proceed with the phone call even if the com log entry creation fails
        window.location.href = `tel:${phoneNumber}`;
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