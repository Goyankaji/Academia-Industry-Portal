document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("applicationSearch");
    const statusFilter = document.getElementById("statusFilter");
    const opportunityFilter = document.getElementById("opportunityFilter");

    /*
     * Client-side search is only used when the table
     * is already loaded. The main filtering is handled
     * by Flask GET parameters.
     */

    if (searchInput) {
        searchInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {
                event.preventDefault();

                const form = this.closest("form");

                if (form) {
                    form.submit();
                }
            }

        });
    }

    /*
     * Automatically submit when status changes.
     */

    if (statusFilter) {
        statusFilter.addEventListener("change", function () {

            const form = this.closest("form");

            if (form) {
                form.submit();
            }

        });
    }

    /*
     * Automatically submit when opportunity changes.
     */

    if (opportunityFilter) {
        opportunityFilter.addEventListener("change", function () {

            const form = this.closest("form");

            if (form) {
                form.submit();
            }

        });
    }

    /*
     * Prevent accidental double submission.
     */

    const filterForm = document.querySelector(".filters-form");

    if (filterForm) {

        filterForm.addEventListener("submit", function () {

            const button = this.querySelector(".filter-button");

            if (button) {
                button.disabled = true;
                button.style.opacity = "0.7";

                const icon = button.querySelector("i");

                if (icon) {
                    icon.className = "fa-solid fa-spinner fa-spin";
                }
            }

        });

    }

});