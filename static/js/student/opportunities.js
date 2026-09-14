document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =====================================================
        // SKILL MATCH PROGRESS BARS
        // =====================================================

        const matchBars =
            document.querySelectorAll(
                ".skill-match-fill"
            );


        matchBars.forEach(
            function (bar) {

                let percentage =
                    parseFloat(
                        bar.dataset.width || "0"
                    );


                // Keep percentage between 0 and 100

                if (percentage < 0) {
                    percentage = 0;
                }

                if (percentage > 100) {
                    percentage = 100;
                }


                // Small delay for animation

                setTimeout(
                    function () {

                        bar.style.width =
                            percentage + "%";

                    },
                    100
                );

            }
        );


        // =====================================================
        // CLIENT SIDE SEARCH
        // =====================================================

        const searchInput =
            document.getElementById(
                "opportunitySearch"
            );

        const opportunityGrid =
            document.getElementById(
                "opportunityGrid"
            );


        if (
            searchInput &&
            opportunityGrid
        ) {

            const cards =
                opportunityGrid.querySelectorAll(
                    ".opportunity-card"
                );


            searchInput.addEventListener(
                "input",
                function () {

                    const searchValue =
                        searchInput.value
                            .trim()
                            .toLowerCase();


                    cards.forEach(
                        function (card) {

                            const title =
                                card.dataset.title || "";

                            const company =
                                card.dataset.company || "";


                            const matches =
                                title.includes(
                                    searchValue
                                )
                                ||
                                company.includes(
                                    searchValue
                                );


                            if (matches) {

                                card.style.display =
                                    "";

                            } else {

                                card.style.display =
                                    "none";

                            }

                        }
                    );

                }
            );

        }


        // =====================================================
        // FILTER FORM
        // =====================================================

        const filterForm =
            document.getElementById(
                "opportunityFilterForm"
            );


        if (filterForm) {

            filterForm.addEventListener(
                "submit",
                function () {

                    const submitButton =
                        filterForm.querySelector(
                            ".filter-btn"
                        );


                    if (submitButton) {

                        submitButton.disabled =
                            true;

                        submitButton.textContent =
                            "Loading...";

                    }

                }
            );

        }


        // =====================================================
        // OPPORTUNITY CARD CLICK FEEDBACK
        // =====================================================

        const detailButtons =
            document.querySelectorAll(
                ".view-opportunity-btn, " +
                ".apply-opportunity-btn"
            );


        detailButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        button.classList.add(
                            "loading"
                        );

                    }
                );

            }
        );


        // =====================================================
        // DEADLINE WARNING
        // =====================================================

        const urgentDeadlines =
            document.querySelectorAll(
                ".deadline-urgent"
            );


        urgentDeadlines.forEach(
            function (deadline) {

                deadline.classList.add(
                    "deadline-pulse"
                );

            }
        );


        // =====================================================
        // SMOOTH CARD APPEARANCE
        // =====================================================

        const cards =
            document.querySelectorAll(
                ".opportunity-card"
            );


        cards.forEach(
            function (card, index) {

                card.style.animationDelay =
                    (index * 0.04) + "s";

                card.classList.add(
                    "opportunity-card-loaded"
                );

            }
        );


        // =====================================================
        // CLEAR SEARCH WHEN CLICKING CLEAR
        // =====================================================

        const clearButton =
            document.querySelector(
                ".clear-filter-btn"
            );


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                function () {

                    if (searchInput) {
                        searchInput.value = "";
                    }

                }
            );

        }


    }
);