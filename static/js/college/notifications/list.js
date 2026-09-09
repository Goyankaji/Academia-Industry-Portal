document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("notificationSearch");
    const filter = document.getElementById("notificationFilter");
    const cards = document.querySelectorAll(".notification-card");
    const filterEmpty = document.getElementById("filterEmpty");

    if (!searchInput || !filter) {
        return;
    }


    function filterNotifications() {

        const searchValue = searchInput.value
            .trim()
            .toLowerCase();

        const filterValue = filter.value;

        let visibleCount = 0;

        cards.forEach(function (card) {

            const searchData = card.dataset.search || "";
            const status = card.dataset.status || "";

            const matchesSearch =
                !searchValue ||
                searchData.includes(searchValue);

            const matchesFilter =
                filterValue === "ALL" ||
                status === filterValue;

            if (matchesSearch && matchesFilter) {

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


    searchInput.addEventListener(
        "input",
        filterNotifications
    );

    filter.addEventListener(
        "change",
        filterNotifications
    );

});