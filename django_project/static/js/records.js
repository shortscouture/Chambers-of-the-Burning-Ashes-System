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


document.addEventListener("DOMContentLoaded", function () {
    const searchButton = document.getElementById("search-button");
    const searchNameInput = document.getElementById("search-name");
    const searchVaultInput = document.getElementById("search-crypt");

    searchButton.addEventListener("click", function () {
        performSearch();
    });

    searchNameInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") performSearch();
    });

    searchVaultInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") performSearch();
    });

    function performSearch() {
        const nameQuery = searchNameInput.value.trim();
        const vaultQuery = searchVaultInput.value.trim();

        const url = new URL(window.location.href);
        url.searchParams.set("search_name", nameQuery);
        url.searchParams.set("search_vault", vaultQuery);

        window.location.href = url.toString();
    }
});
