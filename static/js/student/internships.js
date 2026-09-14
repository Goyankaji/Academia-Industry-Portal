/* =========================================================
   STUDENT INTERNSHIPS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PROGRESS BARS
    ===================================================== */

    const progressBars = document.querySelectorAll(
        ".internship-progress-fill"
    );

    progressBars.forEach(function (bar) {

        let progress = parseFloat(
            bar.getAttribute("data-progress")
        );

        if (isNaN(progress)) {
            progress = 0;
        }

        progress = Math.max(
            0,
            Math.min(100, progress)
        );

        setTimeout(function () {
            bar.style.width = progress + "%";
        }, 100);

    });


    /* =====================================================
       CLIENT-SIDE SEARCH
    ===================================================== */

    const searchInput = document.getElementById(
        "internshipSearch"
    );

    const internshipCards = document.querySelectorAll(
        ".internship-card"
    );

    const noSearchResults = document.getElementById(
        "internshipNoSearchResults"
    );


    if (searchInput && internshipCards.length > 0) {

        searchInput.addEventListener(
            "input",
            function () {

                const searchValue =
                    searchInput.value
                        .trim()
                        .toLowerCase();

                let visibleCount = 0;


                internshipCards.forEach(
                    function (card) {

                        const searchableText =
                            (
                                card.getAttribute(
                                    "data-search"
                                ) || ""
                            ).toLowerCase();


                        if (
                            searchValue === "" ||
                            searchableText.includes(
                                searchValue
                            )
                        ) {

                            card.style.display = "";

                            visibleCount++;

                        } else {

                            card.style.display = "none";

                        }

                    }
                );


                if (noSearchResults) {

                    if (
                        searchValue !== "" &&
                        visibleCount === 0
                    ) {

                        noSearchResults.style.display =
                            "flex";

                    } else {

                        noSearchResults.style.display =
                            "none";

                    }

                }

            }
        );

    }


    /* =====================================================
       CLEAR SEARCH
    ===================================================== */

    const clearSearchButton =
        document.getElementById(
            "clearInternshipSearch"
        );


    if (
        clearSearchButton &&
        searchInput
    ) {

        clearSearchButton.addEventListener(
            "click",
            function () {

                searchInput.value = "";

                searchInput.focus();

                searchInput.dispatchEvent(
                    new Event("input")
                );

            }
        );

    }


    /* =====================================================
       FILTER FORM
    ===================================================== */

    const filterForm =
        document.getElementById(
            "internshipFilterForm"
        );


    if (filterForm) {

        filterForm.addEventListener(
            "submit",
            function () {

                const button =
                    filterForm.querySelector(
                        ".internship-filter-btn"
                    );


                if (button) {

                    button.disabled = true;

                    button.textContent =
                        "Applying...";

                }

            }
        );

    }


    /* =====================================================
       CARD ENTRY ANIMATION
    ===================================================== */

    internshipCards.forEach(
        function (card, index) {

            card.style.opacity = "0";

            card.style.transform =
                "translateY(8px)";

            setTimeout(
                function () {

                    card.style.transition =
                        "opacity 0.3s ease, transform 0.3s ease";

                    card.style.opacity = "1";

                    card.style.transform =
                        "translateY(0)";

                },
                70 * index
            );

        }
    );


    /* =====================================================
       VIEW DETAILS BUTTON FEEDBACK
    ===================================================== */

    const detailButtons =
        document.querySelectorAll(
            ".internship-view-btn"
        );


    detailButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    button.style.opacity = "0.7";

                }
            );

        }
    );


    /* =====================================================
       STATUS FILTER - CLIENT SIDE VISUAL SUPPORT
    ===================================================== */

    const statusSelect =
        document.getElementById(
            "internshipStatus"
        );


    if (
        statusSelect &&
        internshipCards.length > 0
    ) {

        statusSelect.addEventListener(
            "change",
            function () {

                const selectedStatus =
                    statusSelect.value
                        .trim()
                        .toUpperCase();


                if (selectedStatus === "") {

                    internshipCards.forEach(
                        function (card) {

                            card.style.display = "";

                        }
                    );

                    if (noSearchResults) {

                        noSearchResults.style.display =
                            "none";

                    }

                    return;

                }


                let visibleCount = 0;


                internshipCards.forEach(
                    function (card) {

                        const cardStatus =
                            (
                                card.getAttribute(
                                    "data-status"
                                ) || ""
                            ).toUpperCase();


                        if (
                            cardStatus ===
                            selectedStatus
                        ) {

                            card.style.display = "";

                            visibleCount++;

                        } else {

                            card.style.display = "none";

                        }

                    }
                );


                if (noSearchResults) {

                    if (visibleCount === 0) {

                        noSearchResults.style.display =
                            "flex";

                    } else {

                        noSearchResults.style.display =
                            "none";

                    }

                }

            }
        );

    }


    /* =====================================================
       EMPTY STATE
    ===================================================== */

    const emptyState =
        document.querySelector(
            ".internship-empty-state"
        );


    if (
        internshipCards.length === 0 &&
        emptyState
    ) {

        emptyState.classList.add(
            "is-visible"
        );

    }


    /* =====================================================
       INITIALIZE
    ===================================================== */

    console.log(
        "Student Internships JS loaded successfully."
    );

});