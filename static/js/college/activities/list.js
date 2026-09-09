document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("projectSearch");
    const statusFilter = document.getElementById("statusFilter");
    const cards = document.querySelectorAll(".activity-card");
    const filterEmpty = document.getElementById("filterEmpty");

    if (!searchInput || !statusFilter) {
        return;
    }

    function filterProjects() {

        const searchValue = searchInput.value
            .trim()
            .toLowerCase();

        const statusValue = statusFilter.value;

        let visibleCount = 0;

        cards.forEach(function (card) {

            const cardSearch = card.dataset.search || "";
            const cardStatus = card.dataset.status || "";

            const matchesSearch =
                !searchValue ||
                cardSearch.includes(searchValue);

            const matchesStatus =
                statusValue === "ALL" ||
                cardStatus === statusValue;

            if (matchesSearch && matchesStatus) {
                card.style.display = "";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        if (filterEmpty) {
            filterEmpty.style.display =
                visibleCount === 0 ? "block" : "none";
        }
    }

    searchInput.addEventListener("input", filterProjects);
    statusFilter.addEventListener("change", filterProjects);

});