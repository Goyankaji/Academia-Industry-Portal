document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(
        ".filters-form"
    );

    const searchInput = document.querySelector(
        '.filters-form input[name="search"]'
    );

    const companyType = document.querySelector(
        '.filters-form select[name="company_type"]'
    );

    const industrySector = document.querySelector(
        '.filters-form select[name="industry_sector"]'
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

                    if (form) {
                        form.submit();
                    }

                }

            }
        );

    }


    /* =====================================================
       AUTO FILTER - COMPANY TYPE
    ===================================================== */

    if (companyType) {

        companyType.addEventListener(
            "change",
            function () {

                if (form) {
                    form.submit();
                }

            }
        );

    }


    /* =====================================================
       AUTO FILTER - INDUSTRY SECTOR
    ===================================================== */

    if (industrySector) {

        industrySector.addEventListener(
            "change",
            function () {

                if (form) {
                    form.submit();
                }

            }
        );

    }


    /* =====================================================
       PREVENT DOUBLE SUBMISSION
    ===================================================== */

    if (form) {

        form.addEventListener(
            "submit",
            function () {

                const button =
                    form.querySelector(".filter-button");

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


    /* =====================================================
       INDUSTRY CARD HOVER ACCESSIBILITY
    ===================================================== */

    const cards =
        document.querySelectorAll(".industry-card");

    cards.forEach(function (card) {

        card.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    const link =
                        card.querySelector(
                            ".details-button"
                        );

                    if (link) {
                        link.click();
                    }

                }

            }
        );

    });

});