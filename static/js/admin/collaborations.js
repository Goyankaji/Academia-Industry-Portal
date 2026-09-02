/* =========================================================
   SIH ADMIN PORTAL
   COLLABORATIONS MANAGEMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    const searchInput =
        document.getElementById(
            "collaborationSearch"
        );


    const typeFilter =
        document.getElementById(
            "typeFilter"
        );


    const statusFilter =
        document.getElementById(
            "statusFilter"
        );


    const resetFilters =
        document.getElementById(
            "resetFilters"
        );


    const refreshButton =
        document.getElementById(
            "refreshCollaborations"
        );


    const visibleCount =
        document.getElementById(
            "visibleCollaborationCount"
        );


    const activeCount =
        document.getElementById(
            "activeCollaborationCount"
        );


    const pendingCount =
        document.getElementById(
            "pendingCollaborationCount"
        );


    const inactiveCount =
        document.getElementById(
            "inactiveCollaborationCount"
        );


    const emptyRow =
        document.getElementById(
            "filterEmptyRow"
        );


    const rows =
        document.querySelectorAll(
            ".collaboration-row"
        );


    /* =====================================================
       COUNTS
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

            }

            else if (status === "PENDING") {

                pending++;

            }

            else if (status === "INACTIVE") {

                inactive++;

            }

        });


        if (activeCount) {

            activeCount.textContent =
                active;

        }


        if (pendingCount) {

            pendingCount.textContent =
                pending;

        }


        if (inactiveCount) {

            inactiveCount.textContent =
                inactive;

        }

    }


    /* =====================================================
       FILTER
       ===================================================== */

    function applyFilters() {

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


        const status =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        let visible = 0;


        rows.forEach(function (row) {

            const searchable =
                row.dataset.search || "";


            const rowType =
                row.dataset.type || "";


            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                !search ||
                searchable.includes(search);


            const matchesType =
                !type ||
                rowType === type;


            const matchesStatus =
                !status ||
                rowStatus === status;


            const show =
                matchesSearch &&
                matchesType &&
                matchesStatus;


            if (show) {

                row.classList.remove(
                    "hidden"
                );

                visible++;

            }

            else {

                row.classList.add(
                    "hidden"
                );

            }

        });


        if (visibleCount) {

            visibleCount.textContent =
                visible;

        }


        if (emptyRow) {

            if (
                visible === 0 &&
                rows.length > 0
            ) {

                emptyRow.classList.remove(
                    "hidden"
                );

            }

            else {

                emptyRow.classList.add(
                    "hidden"
                );

            }

        }

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


    if (typeFilter) {

        typeFilter.addEventListener(
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


                if (statusFilter) {

                    statusFilter.value = "";

                }


                applyFilters();

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

                window.location.reload();

            }
        );

    }


    /* =====================================================
       INITIAL
       ===================================================== */

    updateCounts();

    applyFilters();


    console.log(
        "SIH Admin Collaborations JS loaded successfully."
    );

});