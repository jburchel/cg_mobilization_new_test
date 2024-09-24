// static/js/form_validation.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.responsive-form');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Basic validation example - you can expand this based on your needs
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    showError(field, 'This field is required');
                } else {
                    clearError(field);
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});

function showError(field, message) {
    const errorElement = field.parentElement.querySelector('.error-message') || document.createElement('div');
    errorElement.textContent = message;
    errorElement.classList.add('error-message');
    if (!field.parentElement.querySelector('.error-message')) {
        field.parentElement.appendChild(errorElement);
    }
}

function clearError(field) {
    const errorElement = field.parentElement.querySelector('.error-message');
    if (errorElement) {
        errorElement.remove();
    }
}