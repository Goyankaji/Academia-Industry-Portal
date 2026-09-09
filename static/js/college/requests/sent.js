document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("requestSearch");
    const statusFilter = document.getElementById("statusFilter");
    const cards = document.querySelectorAll(".request-card");
    const noResults = document.getElementById("noResults");

    function filterRequests() {

        const searchValue = (searchInput?.value || "")
            .toLowerCase()
            .trim();

        const statusValue = (statusFilter?.value || "")
            .toLowerCase()
            .trim();

        let visibleCount = 0;

        cards.forEach(card => {

            const company = card.dataset.company || "";
            const title = card.dataset.title || "";
            const type = card.dataset.type || "";
            const status = card.dataset.status || "";

            const matchesSearch =
                !searchValue ||
                company.includes(searchValue) ||
                title.includes(searchValue) ||
                type.includes(searchValue);

            const matchesStatus =
                !statusValue || status === statusValue;

            if (matchesSearch && matchesStatus) {
                card.style.display = "block";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        if (noResults) {
            noResults.classList.toggle("hidden", visibleCount !== 0);
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", filterRequests);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", filterRequests);
    }

});