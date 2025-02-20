document.addEventListener("DOMContentLoaded", () => {
    function sortTable(columnClass, isNumeric = false, isBoolean = false) {
        const table = document.querySelector("tbody");
        const rows = Array.from(table.querySelectorAll("tr"));
        let ascending = true;

        return function () {
            rows.sort((rowA, rowB) => {
                let cellA = rowA.querySelector(`.${columnClass}`).textContent.trim();
                let cellB = rowB.querySelector(`.${columnClass}`).textContent.trim();

                if (isNumeric) {
                    return ascending ? Number(cellA) - Number(cellB) : Number(cellB) - Number(cellA);
                } else if (isBoolean) {
                    return ascending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
                } else {
                    return ascending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
                }
            });

            table.innerHTML = "";
            rows.forEach(row => table.appendChild(row));

            ascending = !ascending;
        };
    }

    document.getElementById("sort-vault").addEventListener("click", sortTable("vault-id", true));
    document.getElementById("sort-customer").addEventListener("click", sortTable("check-customer", false, true));
    document.getElementById("sort-beneficiary").addEventListener("click", sortTable("check-beneficiary", false, true));
    document.getElementById("sort-record").addEventListener("click", sortTable("check-record", false, true));
    document.getElementById("sort-payment").addEventListener("click", sortTable("check-payment", false, true));
    document.getElementById("sort-privilege").addEventListener("click", sortTable("check-privilege", false, true));
});
