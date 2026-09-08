document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       STUDENT DIRECTORY FILTERS
       ========================================================= */

    const filterForm =
        document.getElementById("studentFilterForm");

    const courseFilter =
        document.getElementById("courseFilter");

    const branchFilter =
        document.getElementById("branchFilter");

    const collegeFilter =
        document.getElementById("collegeFilter");


    /*
     * Automatically submit when Course changes
     */
    if (courseFilter) {

        courseFilter.addEventListener("change", function () {

            if (filterForm) {
                filterForm.submit();
            }

        });

    }


    /*
     * Automatically submit when Branch changes
     */
    if (branchFilter) {

        branchFilter.addEventListener("change", function () {

            if (filterForm) {
                filterForm.submit();
            }

        });

    }


    /*
     * Automatically submit when College changes
     */
    if (collegeFilter) {

        collegeFilter.addEventListener("change", function () {

            if (filterForm) {
                filterForm.submit();
            }

        });

    }


    /* =========================================================
       SEARCH
       ========================================================= */

    const searchInput =
        document.getElementById("studentSearch");


    /*
     * Search when Enter is pressed
     */
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


    /* =========================================================
       FORM LOADING STATE
       ========================================================= */

    if (filterForm) {

        filterForm.addEventListener(
            "submit",
            function () {

                const submitButton =
                    filterForm.querySelector(
                        ".btn-primary"
                    );


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.textContent =
                        "Searching...";

                }

            }
        );

    }


    /* =========================================================
       SKILL ASSESSMENT PROGRESS BARS
       ========================================================= */

    const progressBars =
        document.querySelectorAll(
            ".skill-progress-bar"
        );


    progressBars.forEach(function (bar) {

        /*
         * Get assessment percentage from
         * data-percentage attribute
         */
        const percentage =
            parseFloat(
                bar.dataset.percentage
            );


        /*
         * Only process valid numbers
         */
        if (!isNaN(percentage)) {

            /*
             * Keep percentage between 0 and 100
             */
            const safePercentage =
                Math.min(
                    Math.max(percentage, 0),
                    100
                );


            /*
             * Apply progress width
             */
            bar.style.width =
                safePercentage + "%";

        }

    });


});