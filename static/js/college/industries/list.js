document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("industrySearch");
    const typeFilter = document.getElementById("typeFilter");
    const cards = document.querySelectorAll(".industry-card");
    const noResults = document.getElementById("noResults");

    function filterIndustries() {

        const searchValue = (searchInput?.value || "").toLowerCase().trim();
        const typeValue = (typeFilter?.value || "").toLowerCase().trim();

        let visibleCount = 0;

        cards.forEach(card => {

            const name = card.dataset.name || "";
            const code = card.dataset.code || "";
            const type = card.dataset.type || "";
            const city = card.dataset.city || "";

            const matchesSearch =
                !searchValue ||
                name.includes(searchValue) ||
                code.includes(searchValue) ||
                type.includes(searchValue) ||
                city.includes(searchValue);

            const matchesType =
                !typeValue || type === typeValue;

            if (matchesSearch && matchesType) {
                card.style.display = "flex";
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
        searchInput.addEventListener("input", filterIndustries);
    }

    if (typeFilter) {
        typeFilter.addEventListener("change", filterIndustries);
    }

});