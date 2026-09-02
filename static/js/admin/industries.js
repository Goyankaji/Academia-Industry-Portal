/* =========================================================
   SIH ADMIN PORTAL
   INDUSTRIES MANAGEMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const searchInput =
        document.getElementById("industrySearch");

    const typeFilter =
        document.getElementById("typeFilter");

    const sectorFilter =
        document.getElementById("sectorFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetFilters =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshIndustries");

    const visibleCount =
        document.getElementById("visibleIndustryCount");

    const activeCount =
        document.getElementById("activeIndustryCount");

    const pendingCount =
        document.getElementById("pendingIndustryCount");

    const inactiveCount =
        document.getElementById("inactiveIndustryCount");

    const emptyRow =
        document.getElementById("filterEmptyRow");

    const rows =
        document.querySelectorAll(".industry-row");


    /* =====================================================
       STATUS COUNTS
       ===================================================== */

    function updateCounts() {

        let active = 0;
        let pending = 0;
        let inactive = 0;


        rows.forEach(function (row) {

            const status =
                row.dataset.status || "";


            if (status === "ACTIVE") {

                active++;

            } else if (status === "PENDING") {

                pending++;

            } else if (status === "INACTIVE") {

                inactive++;

            }

        });


        if (activeCount) {
            activeCount.textContent = active;
        }


        if (pendingCount) {
            pendingCount.textContent = pending;
        }


        if (inactiveCount) {
            inactiveCount.textContent = inactive;
        }

    }


    /* =====================================================
       FILTER INDUSTRIES
       ===================================================== */

    function filterIndustries() {

        const search =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const type =
            typeFilter
                ? typeFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const sector =
            sectorFilter
                ? sectorFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const status =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        let visibleIndustries = 0;


        rows.forEach(function (row) {

            const name =
                row.dataset.name || "";

            const contact =
                row.dataset.contact || "";

            const email =
                row.dataset.email || "";

            const rowType =
                row.dataset.type || "";

            const rowSector =
                row.dataset.sector || "";

            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                !search ||
                name.includes(search) ||
                contact.includes(search) ||
                email.includes(search);


            const matchesType =
                !type ||
                rowType === type;


            const matchesSector =
                !sector ||
                rowSector === sector;


            const matchesStatus =
                !status ||
                rowStatus === status;


            const shouldShow =
                matchesSearch &&
                matchesType &&
                matchesSector &&
                matchesStatus;


            if (shouldShow) {

                row.classList.remove("hidden");

                visibleIndustries++;

            } else {

                row.classList.add("hidden");

            }

        });


        if (visibleCount) {

            visibleCount.textContent =
                visibleIndustries;

        }


        if (emptyRow) {

            if (
                visibleIndustries === 0 &&
                rows.length > 0
            ) {

                emptyRow.classList.remove("hidden");

            } else {

                emptyRow.classList.add("hidden");

            }

        }

    }


    /* =====================================================
       EVENTS
       ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterIndustries
        );

    }


    if (typeFilter) {

        typeFilter.addEventListener(
            "change",
            filterIndustries
        );

    }


    if (sectorFilter) {

        sectorFilter.addEventListener(
            "change",
            filterIndustries
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterIndustries
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

                if (typeFilter) {
                    typeFilter.value = "";
                }

                if (sectorFilter) {
                    sectorFilter.value = "";
                }

                if (statusFilter) {
                    statusFilter.value = "";
                }

                filterIndustries();

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

                }, 300);

            }
        );

    }


    /* =====================================================
       INITIAL
       ===================================================== */

    updateCounts();

    filterIndustries();


    console.log(
        "SIH Admin Industries JS loaded successfully."
    );

});