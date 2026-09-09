document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("departmentSearch");

    const statusFilter =
        document.getElementById("statusFilter");

    const cards =
        document.querySelectorAll(".department-card");

    const emptyState =
        document.getElementById("departmentEmpty");


    function filterDepartments() {

        const search =
            (searchInput?.value || "")
                .trim()
                .toLowerCase();

        const status =
            statusFilter?.value || "ALL";

        let visibleCount = 0;

        cards.forEach(function (card) {

            const name =
                card.dataset.name || "";

            const code =
                card.dataset.code || "";

            const cardStatus =
                card.dataset.status || "";

            const matchesSearch =
                name.includes(search) ||
                code.includes(search);

            const matchesStatus =
                status === "ALL" ||
                cardStatus === status;

            if (matchesSearch && matchesStatus) {

                card.style.display = "flex";
                visibleCount++;

            } else {

                card.style.display = "none";

            }

        });

        if (emptyState) {
            emptyState.style.display =
                visibleCount === 0
                    ? "block"
                    : "none";
        }
    }


    if (searchInput) {
        searchInput.addEventListener(
            "input",
            filterDepartments
        );
    }


    if (statusFilter) {
        statusFilter.addEventListener(
            "change",
            filterDepartments
        );
    }


    /* Delete confirmation */

    document
        .querySelectorAll(".delete-form")
        .forEach(function (form) {

            form.addEventListener(
                "submit",
                function (event) {

                    const confirmed =
                        window.confirm(
                            "Are you sure you want to delete this department?"
                        );

                    if (!confirmed) {
                        event.preventDefault();
                    }

                }
            );

        });


    console.log(
        "SIH College Departments List loaded successfully."
    );

});