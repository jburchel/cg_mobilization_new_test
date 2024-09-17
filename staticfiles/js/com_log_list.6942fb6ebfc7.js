document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const tableBody = document.getElementById('comLogTableBody');
    const originalRows = Array.from(tableBody.querySelectorAll('tr'));

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        const filteredRows = originalRows.filter(row => {
            return Array.from(row.cells).some(cell => 
                cell.textContent.toLowerCase().includes(searchTerm)
            );
        });

        tableBody.innerHTML = '';
        filteredRows.forEach(row => tableBody.appendChild(row));

        if (filteredRows.length === 0) {
            const noResultsRow = document.createElement('tr');
            const noResultsCell = document.createElement('td');
            noResultsCell.colSpan = 6;
            noResultsCell.textContent = 'No communications found.';
            noResultsRow.appendChild(noResultsCell);
            tableBody.appendChild(noResultsRow);
        }
    });
});