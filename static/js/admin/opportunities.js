/* =========================================================
   SIH ADMIN PORTAL
   OPPORTUNITIES JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("opportunitySearch");

    const industryFilter =
        document.getElementById("industryFilter");

    const typeFilter =
        document.getElementById("typeFilter");

    const workModeFilter =
        document.getElementById("workModeFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetButton =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshOpportunities");

    const rows =
        document.querySelectorAll(".opportunity-row");

    const visibleCount =
        document.getElementById("visibleOpportunityCount");

    const totalCount =
        document.getElementById("totalOpportunities");

    const openCount =
        document.getElementById("openOpportunities");

    const draftCount =
        document.getElementById("draftOpportunities");

    const closedCount =
        document.getElementById("closedOpportunities");


    /* =====================================================
       UPDATE STATISTICS
       ===================================================== */

    function updateStatistics() {

        let open = 0;
        let draft = 0;
        let closed = 0;

        rows.forEach(function (row) {

            const status =
                row.dataset.status;

            if (status === "OPEN") {
                open++;
            }

            if (status === "DRAFT") {
                draft++;
            }

            if (status === "CLOSED") {
                closed++;
            }

        });


        if (totalCount) {
            totalCount.textContent = rows.length;
        }

        if (openCount) {
            openCount.textContent = open;
        }

        if (draftCount) {
            draftCount.textContent = draft;
        }

        if (closedCount) {
            closedCount.textContent = closed;
        }

    }


    /* =====================================================
       FILTER
       ===================================================== */

    function applyFilters() {

        const search =
            searchInput.value
                .trim()
                .toLowerCase();

        const industry =
            industryFilter.value;

        const type =
            typeFilter.value;

        const workMode =
            workModeFilter.value;

        const status =
            statusFilter.value;


        let visible = 0;


        rows.forEach(function (row) {

            const rowSearch =
                row.dataset.search || "";

            const rowIndustry =
                row.dataset.industry || "";

            const rowType =
                row.dataset.type || "";

            const rowWorkMode =
                row.dataset.workMode || "";

            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                !search ||
                rowSearch.includes(search);

            const matchesIndustry =
                !industry ||
                rowIndustry === industry;

            const matchesType =
                !type ||
                rowType === type;

            const matchesWorkMode =
                !workMode ||
                rowWorkMode === workMode;

            const matchesStatus =
                !status ||
                rowStatus === status;


            const matches =
                matchesSearch &&
                matchesIndustry &&
                matchesType &&
                matchesWorkMode &&
                matchesStatus;


            if (matches) {

                row.classList.remove("hidden");

                visible++;

            } else {

                row.classList.add("hidden");

            }

        });


        if (visibleCount) {
            visibleCount.textContent = visible;
        }

    }


    /* =====================================================
       RESET
       ===================================================== */

    function resetFilters() {

        searchInput.value = "";

        industryFilter.value = "";

        typeFilter.value = "";

        workModeFilter.value = "";

        statusFilter.value = "";

        applyFilters();

    }


    /* =====================================================
       REFRESH
       ===================================================== */

    function refreshPage() {

        window.location.reload();

    }


    /* =====================================================
       EVENTS
       ===================================================== */

    if (searchInput) {
        searchInput.addEventListener(
            "input",
            applyFilters
        );
    }

    if (industryFilter) {
        industryFilter.addEventListener(
            "change",
            applyFilters
        );
    }

    if (typeFilter) {
        typeFilter.addEventListener(
            "change",
            applyFilters
        );
    }

    if (workModeFilter) {
        workModeFilter.addEventListener(
            "change",
            applyFilters
        );
    }

    if (statusFilter) {
        statusFilter.addEventListener(
            "change",
            applyFilters
        );
    }

    if (resetButton) {
        resetButton.addEventListener(
            "click",
            resetFilters
        );
    }

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            refreshPage
        );
    }


    /* =====================================================
       INITIAL LOAD
       ===================================================== */

    updateStatistics();

    applyFilters();


    console.log(
        "SIH Admin Opportunities JS loaded successfully."
    );

});