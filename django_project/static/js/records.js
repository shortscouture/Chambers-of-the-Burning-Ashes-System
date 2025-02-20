document.addEventListener("DOMContentLoaded", function () {
    const table = document.querySelector("table");
    const headers = document.querySelectorAll("th.sortable");

    headers.forEach((header, index) => {
        header.addEventListener("click", function () {
            sortTable(index);
        });
    });

    function sortTable(columnIndex) {
        let tbody = table.querySelector("tbody");
        let rows = Array.from(tbody.querySelectorAll("tr"));
        let isAscending = table.dataset.sortOrder === "asc";

        rows.sort((rowA, rowB) => {
            let cellA = rowA.cells[columnIndex].textContent.trim();
            let cellB = rowB.cells[columnIndex].textContent.trim();

            // Convert to numbers if applicable
            let a = isNaN(cellA) ? cellA.toLowerCase() : parseFloat(cellA);
            let b = isNaN(cellB) ? cellB.toLowerCase() : parseFloat(cellB);

            return isAscending ? (a > b ? 1 : -1) : (a < b ? 1 : -1);
        });

        // Toggle sorting order
        table.dataset.sortOrder = isAscending ? "desc" : "asc";

        // Reinsert sorted rows
        tbody.append(...rows);
    }
});
