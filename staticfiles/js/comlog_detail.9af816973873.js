document.addEventListener('DOMContentLoaded', function() {
    // Function to confirm before deleting a com log
    function confirmDelete(event) {
        if (!confirm('Are you sure you want to delete this communication log?')) {
            event.preventDefault();
        }
    }

    // Add event listener to delete button if it exists
    const deleteButton = document.querySelector('.btn-delete');
    if (deleteButton) {
        deleteButton.addEventListener('click', confirmDelete);
    }

    // Function to copy com log summary to clipboard
    function copySummary() {
        const summaryText = document.querySelector('.additional-info p').textContent;
        navigator.clipboard.writeText(summaryText).then(() => {
            alert('Summary copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }

    // Add event listener to a "Copy Summary" button if it exists
    const copyButton = document.querySelector('.btn-copy-summary');
    if (copyButton) {
        copyButton.addEventListener('click', copySummary);
    }
});