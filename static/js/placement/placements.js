document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.querySelector(
        '.filters-form input[name="search"]'
    );

    const branchFilter = document.querySelector(
        '.filters-form select[name="branch"]'
    );

    const companyFilter = document.querySelector(
        '.filters-form select[name="company_id"]'
    );

    const filterForm = document.querySelector(
        ".filters-form"
    );


    /* =====================================================
       ENTER TO SEARCH
    ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    if (filterForm) {
                        filterForm.submit();
                    }

                }

            }
        );

    }


    /* =====================================================
       AUTO FILTER - BRANCH
    ===================================================== */

    if (branchFilter) {

        branchFilter.addEventListener(
            "change",
            function () {

                if (filterForm) {
                    filterForm.submit();
                }

            }
        );

    }


    /* =====================================================
       AUTO FILTER - COMPANY
    ===================================================== */

    if (companyFilter) {

        companyFilter.addEventListener(
            "change",
            function () {

                if (filterForm) {
                    filterForm.submit();
                }

            }
        );

    }


    /* =====================================================
       PREVENT DOUBLE SUBMISSION
    ===================================================== */

    if (filterForm) {

        filterForm.addEventListener(
            "submit",
            function () {

                const button =
                    this.querySelector(".filter-button");

                if (button) {

                    button.disabled = true;

                    button.style.opacity = "0.7";

                    const icon =
                        button.querySelector("i");

                    if (icon) {

                        icon.className =
                            "fa-solid fa-spinner fa-spin";

                    }

                }

            }
        );

    }

});