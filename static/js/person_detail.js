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

    // Create the initial com log entry
    createComLog(personId, communicationType, notes)
        .then(logId => {
            console.log('Com log entry created:', logId);
            if (action === 'phone') {
                window.location.href = `tel:${phoneNumber}`;
                // After the call, redirect to edit the log
                setTimeout(() => {
                    window.location.href = `/com_log/${logId}/edit/`;
                }, 1000); // Wait for 1 second to allow the call to be initiated
            } else {
                // For text, open a modal to input the message
                openTextModal(personId, phoneNumber, logId);
            }
        })
        .catch(error => {
            console.error('Error creating com log entry:', error);
            // Proceed with the communication even if logging fails
            if (action === 'phone') {
                window.location.href = `tel:${phoneNumber}`;
            } else {
                window.location.href = `sms:${phoneNumber}`;
            }
        });
}

function createComLog(personId, communicationType, notes) {
    return fetch('/com_log/api/create/', {
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
    .then(data => data.id);  // Assuming the API returns the ID of the created log
}

function openTextModal(personId, phoneNumber, logId) {
    // Create and show a modal for text input
    const modal = document.createElement('div');
    modal.className = 'text-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Text Message</h2>
            <textarea id="text-message" rows="4" placeholder="Enter your message"></textarea>
            <button id="send-text">Send</button>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('send-text').addEventListener('click', function() {
        const message = document.getElementById('text-message').value;
        updateComLog(logId, message)
            .then(() => {
                window.location.href = `sms:${phoneNumber}?body=${encodeURIComponent(message)}`;
                modal.remove();
            })
            .catch(error => {
                console.error('Error updating com log entry:', error);
                window.location.href = `sms:${phoneNumber}?body=${encodeURIComponent(message)}`;
                modal.remove();
            });
    });
}

function updateComLog(logId, notes) {
    return fetch(`/com_log/api/update/${logId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            notes: notes
        })
    })
    .then(response => response.json());
}

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