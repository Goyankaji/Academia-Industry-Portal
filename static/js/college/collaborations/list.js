document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("collaborationSearch");

    const statusFilter =
        document.getElementById("statusFilter");

    const cards =
        document.querySelectorAll(".collaboration-card");

    const noResults =
        document.getElementById("noResults");


    function filterCollaborations() {

        const searchValue =
            (searchInput?.value || "")
                .toLowerCase()
                .trim();

        const statusValue =
            (statusFilter?.value || "")
                .toLowerCase()
                .trim();


        let visibleCount = 0;


        cards.forEach(card => {

            const company =
                card.dataset.company || "";

            const title =
                card.dataset.title || "";

            const type =
                card.dataset.type || "";

            const status =
                card.dataset.status || "";


            const matchesSearch =
                !searchValue ||
                company.includes(searchValue) ||
                title.includes(searchValue) ||
                type.includes(searchValue);


            const matchesStatus =
                !statusValue ||
                status === statusValue;


            if (matchesSearch && matchesStatus) {

                card.style.display = "flex";
                visibleCount++;

            } else {

                card.style.display = "none";

            }

        });


        if (noResults) {

            noResults.classList.toggle(
                "hidden",
                visibleCount !== 0
            );

        }

    }


    searchInput?.addEventListener(
        "input",
        filterCollaborations
    );


    statusFilter?.addEventListener(
        "change",
        filterCollaborations
    );

});