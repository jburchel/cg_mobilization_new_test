document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const tableBody = document.getElementById('comLogTableBody');
    const originalRows = Array.from(tableBody.querySelectorAll('tr'));
    const noResultsMessage = document.createElement('tr');
    noResultsMessage.innerHTML = '<td colspan="6">No communications found.</td>';

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        const filteredRows = originalRows.filter(row => {
            return Array.from(row.cells).some(cell => 
                cell.textContent.toLowerCase().includes(searchTerm)
            );
        });

        tableBody.innerHTML = '';

        if (filteredRows.length === 0) {
            tableBody.appendChild(noResultsMessage);
        } else {
            filteredRows.forEach(row => tableBody.appendChild(row));
        }
    });

    // Add touch support for mobile devices
    searchInput.addEventListener('touchstart', function() {
        this.focus();
    });
});