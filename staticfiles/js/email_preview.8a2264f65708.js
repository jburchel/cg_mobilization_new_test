document.addEventListener('DOMContentLoaded', function() {
    const bodyInput = document.getElementById('id_body');
    const previewDiv = document.getElementById('email-body-preview');

    if (bodyInput && previewDiv) {
        bodyInput.addEventListener('input', function() {
            previewDiv.innerHTML = this.value.replace(/\n/g, '<br>');
        });

        // Trigger the event once to initialize the preview
        bodyInput.dispatchEvent(new Event('input'));
    } else {
        console.error('Email body input or preview div not found');
    }
});