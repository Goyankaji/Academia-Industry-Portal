/* =========================================================
   SIH ADMIN PORTAL
   PROJECTS MANAGEMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const searchInput =
        document.getElementById("projectSearch");

    const collegeFilter =
        document.getElementById("collegeFilter");

    const industryFilter =
        document.getElementById("industryFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetFilters =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshProjects");

    const visibleCount =
        document.getElementById("visibleProjectCount");

    const filterEmptyRow =
        document.getElementById("filterEmptyRow");

    const rows =
        document.querySelectorAll(".project-row");

    const activeCount =
        document.getElementById("activeProjectCount");

    const pendingCount =
        document.getElementById("pendingProjectCount");

    const completedCount =
        document.getElementById("completedProjectCount");


    /* =====================================================
       KPI COUNTS
       ===================================================== */

    function updateCounts() {

        let active = 0;

        let pending = 0;

        let completed = 0;


        rows.forEach(function (row) {

            const status =
                (row.dataset.status || "").toUpperCase();


            if (status === "ACTIVE") {

                active++;

            }

            else if (status === "PENDING") {

                pending++;

            }

            else if (status === "COMPLETED") {

                completed++;

            }

        });


        if (activeCount) {

            activeCount.textContent = active;

        }


        if (pendingCount) {

            pendingCount.textContent = pending;

        }


        if (completedCount) {

            completedCount.textContent = completed;

        }

    }


    /* =====================================================
       FILTER PROJECTS
       ===================================================== */

    function filterProjects() {

        const search =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const college =
            collegeFilter
                ? collegeFilter.value
                : "";


        const industry =
            industryFilter
                ? industryFilter.value
                : "";


        const status =
            statusFilter
                ? statusFilter.value.toUpperCase()
                : "";


        let visibleProjects = 0;


        rows.forEach(function (row) {


            const name =
                row.dataset.name || "";


            const student =
                row.dataset.student || "";


            const industryName =
                row.dataset.industry || "";


            const collegeId =
                row.dataset.collegeId || "";


            const industryId =
                row.dataset.industryId || "";


            const rowStatus =
                (row.dataset.status || "").toUpperCase();


            const matchesSearch =
                !search ||
                name.includes(search) ||
                student.includes(search) ||
                industryName.includes(search);


            const matchesCollege =
                !college ||
                collegeId === college;


            const matchesIndustry =
                !industry ||
                industryId === industry;


            const matchesStatus =
                !status ||
                rowStatus === status;


            const visible =
                matchesSearch &&
                matchesCollege &&
                matchesIndustry &&
                matchesStatus;


            if (visible) {

                row.classList.remove("hidden");

                visibleProjects++;

            }

            else {

                row.classList.add("hidden");

            }

        });


        if (visibleCount) {

            visibleCount.textContent =
                visibleProjects;

        }


        if (filterEmptyRow) {

            if (
                visibleProjects === 0 &&
                rows.length > 0
            ) {

                filterEmptyRow.classList.remove("hidden");

            }

            else {

                filterEmptyRow.classList.add("hidden");

            }

        }

    }


    /* =====================================================
       SEARCH
       ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterProjects
        );

    }


    /* =====================================================
       FILTER EVENTS
       ===================================================== */

    if (collegeFilter) {

        collegeFilter.addEventListener(
            "change",
            filterProjects
        );

    }


    if (industryFilter) {

        industryFilter.addEventListener(
            "change",
            filterProjects
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterProjects
        );

    }


    /* =====================================================
       RESET
       ===================================================== */

    if (resetFilters) {

        resetFilters.addEventListener(
            "click",
            function () {

                if (searchInput) {

                    searchInput.value = "";

                }


                if (collegeFilter) {

                    collegeFilter.value = "";

                }


                if (industryFilter) {

                    industryFilter.value = "";

                }


                if (statusFilter) {

                    statusFilter.value = "";

                }


                filterProjects();

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

                refreshButton.disabled = true;

                refreshButton.classList.add("loading");

                setTimeout(function () {

                    window.location.reload();

                }, 300);

            }
        );

    }


    /* =====================================================
       INITIAL
       ===================================================== */

    updateCounts();

    filterProjects();


    console.log(
        "SIH Admin Projects JS loaded successfully."
    );

});