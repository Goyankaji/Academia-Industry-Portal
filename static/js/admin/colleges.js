/* =========================================================
   SIH ADMIN PORTAL
   COLLEGES MANAGEMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const searchInput =
        document.getElementById("collegeSearch");

    const clearSearch =
        document.getElementById("clearSearch");

    const stateFilter =
        document.getElementById("stateFilter");

    const cityFilter =
        document.getElementById("cityFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetFilters =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshColleges");

    const visibleCount =
        document.getElementById("visibleCollegeCount");

    const filterEmptyRow =
        document.getElementById("filterEmptyRow");

    const collegeRows =
        document.querySelectorAll(".college-row");


    /* =====================================================
       FILTER COLLEGES
       ===================================================== */

    function filterColleges() {

        const search =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const state =
            stateFilter
                ? stateFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const city =
            cityFilter
                ? cityFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const status =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        let visibleColleges = 0;


        collegeRows.forEach(function (row) {


            const name =
                row.dataset.name || "";


            const code =
                row.dataset.code || "";


            const university =
                row.dataset.university || "";


            const rowState =
                row.dataset.state || "";


            const rowCity =
                row.dataset.city || "";


            const rowStatus =
                row.dataset.status || "";


            /* SEARCH */

            const matchesSearch =
                !search ||
                name.includes(search) ||
                code.includes(search) ||
                university.includes(search);


            /* STATE */

            const matchesState =
                !state ||
                rowState === state;


            /* CITY */

            const matchesCity =
                !city ||
                rowCity === city;


            /* STATUS */

            const matchesStatus =
                !status ||
                rowStatus === status;


            const shouldShow =
                matchesSearch &&
                matchesState &&
                matchesCity &&
                matchesStatus;


            if (shouldShow) {

                row.classList.remove("hidden");

                visibleColleges++;

            } else {

                row.classList.add("hidden");

            }

        });


        if (visibleCount) {

            visibleCount.textContent =
                visibleColleges;

        }


        if (filterEmptyRow) {

            if (
                visibleColleges === 0 &&
                collegeRows.length > 0
            ) {

                filterEmptyRow.classList.remove("hidden");

            } else {

                filterEmptyRow.classList.add("hidden");

            }

        }


        if (clearSearch) {

            if (
                searchInput &&
                searchInput.value.trim()
            ) {

                clearSearch.classList.add("visible");

            } else {

                clearSearch.classList.remove("visible");

            }

        }

    }


    /* =====================================================
       SEARCH
       ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterColleges
        );

    }


    /* =====================================================
       FILTER EVENTS
       ===================================================== */

    if (stateFilter) {

        stateFilter.addEventListener(
            "change",
            filterColleges
        );

    }


    if (cityFilter) {

        cityFilter.addEventListener(
            "change",
            filterColleges
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterColleges
        );

    }


    /* =====================================================
       CLEAR SEARCH
       ===================================================== */

    if (clearSearch) {

        clearSearch.addEventListener(
            "click",
            function () {

                if (searchInput) {

                    searchInput.value = "";

                    filterColleges();

                    searchInput.focus();

                }

            }
        );

    }


    /* =====================================================
       RESET FILTERS
       ===================================================== */

    if (resetFilters) {

        resetFilters.addEventListener(
            "click",
            function () {

                if (searchInput) {
                    searchInput.value = "";
                }

                if (stateFilter) {
                    stateFilter.value = "";
                }

                if (cityFilter) {
                    cityFilter.value = "";
                }

                if (statusFilter) {
                    statusFilter.value = "";
                }

                filterColleges();

            }
        );

    }


    /* =====================================================
       REFRESH
       ===================================================== */

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            function () {

                refreshButton.classList.add(
                    "loading"
                );

                refreshButton.disabled = true;


                setTimeout(function () {

                    window.location.reload();

                }, 350);

            }
        );

    }


    /* =====================================================
       INITIAL FILTER
       ===================================================== */

    filterColleges();


    /* =====================================================
       LOG
       ===================================================== */

    console.log(
        "SIH Admin Colleges JS loaded successfully."
    );

});