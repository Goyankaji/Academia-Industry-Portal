/* =========================================================
   SIH ADMIN PORTAL
   STUDENTS MANAGEMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
       ===================================================== */

    const searchInput =
        document.getElementById("studentSearch");

    const clearSearch =
        document.getElementById("clearSearch");

    const collegeFilter =
        document.getElementById("collegeFilter");

    const branchFilter =
        document.getElementById("branchFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetFilters =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshStudents");

    const visibleCount =
        document.getElementById("visibleStudentCount");

    const filterEmptyRow =
        document.getElementById("filterEmptyRow");

    const studentRows =
        document.querySelectorAll(".student-row");


    /* =====================================================
       FILTER STUDENTS
       ===================================================== */

    function filterStudents() {

        const search =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";

        const college =
            collegeFilter
                ? collegeFilter.value
                    .trim()
                    .toLowerCase()
                : "";

        const branch =
            branchFilter
                ? branchFilter.value
                    .trim()
                    .toLowerCase()
                : "";

        const status =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        let visibleStudents = 0;


        studentRows.forEach(function (row) {

            const name =
                row.dataset.name || "";

            const email =
                row.dataset.email || "";

            const enrollment =
                row.dataset.enrollment || "";

            const rowCollege =
                row.dataset.college || "";

            const rowBranch =
                row.dataset.branch || "";

            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                !search ||
                name.includes(search) ||
                email.includes(search) ||
                enrollment.includes(search);


            const matchesCollege =
                !college ||
                rowCollege === college;


            const matchesBranch =
                !branch ||
                rowBranch === branch;


            const matchesStatus =
                !status ||
                rowStatus === status;


            const shouldShow =
                matchesSearch &&
                matchesCollege &&
                matchesBranch &&
                matchesStatus;


            if (shouldShow) {

                row.classList.remove("hidden");

                visibleStudents++;

            } else {

                row.classList.add("hidden");

            }

        });


        if (visibleCount) {

            visibleCount.textContent =
                visibleStudents;

        }


        if (filterEmptyRow) {

            if (
                visibleStudents === 0 &&
                studentRows.length > 0
            ) {

                filterEmptyRow.classList.remove("hidden");

            } else {

                filterEmptyRow.classList.add("hidden");

            }

        }


        if (clearSearch) {

            if (searchInput.value.trim()) {

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
            filterStudents
        );

    }


    /* =====================================================
       FILTER EVENTS
       ===================================================== */

    if (collegeFilter) {

        collegeFilter.addEventListener(
            "change",
            filterStudents
        );

    }


    if (branchFilter) {

        branchFilter.addEventListener(
            "change",
            filterStudents
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterStudents
        );

    }


    /* =====================================================
       CLEAR SEARCH
       ===================================================== */

    if (clearSearch) {

        clearSearch.addEventListener(
            "click",
            function () {

                searchInput.value = "";

                filterStudents();

                searchInput.focus();

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

                if (collegeFilter) {
                    collegeFilter.value = "";
                }

                if (branchFilter) {
                    branchFilter.value = "";
                }

                if (statusFilter) {
                    statusFilter.value = "";
                }

                filterStudents();

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

                refreshButton.classList.add("loading");

                refreshButton.disabled = true;

                setTimeout(function () {

                    window.location.reload();

                }, 350);

            }
        );

    }


    /* =====================================================
       BACKLOG COUNT
       ===================================================== */

    const backlogCount =
        document.getElementById(
            "backlogStudentCount"
        );


    if (backlogCount) {

        let count = 0;


        studentRows.forEach(function (row) {

            const backlogs =
                parseInt(
                    row.dataset.backlogs || "0",
                    10
                );


            if (backlogs > 0) {

                count++;

            }

        });


        backlogCount.textContent = count;

    }


    /* =====================================================
       INITIAL FILTER
       ===================================================== */

    filterStudents();


    /* =====================================================
       LOG
       ===================================================== */

    console.log(
        "SIH Admin Students JS loaded successfully."
    );

});