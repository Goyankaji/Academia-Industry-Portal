document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("searchInput");

    const collegeFilter =
        document.getElementById("collegeFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetFilters =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshPlacementCells");

    const rows =
        document.querySelectorAll(".placement-row");

    const resultCount =
        document.getElementById("resultCount");

    const activeCount =
        document.getElementById("activeCount");

    const pendingCount =
        document.getElementById("pendingCount");

    const inactiveCount =
        document.getElementById("inactiveCount");


    function updateCounts() {

        let active = 0;
        let pending = 0;
        let inactive = 0;

        rows.forEach(function (row) {

            const status =
                row.dataset.status;

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
            activeCount.textContent = active;
        }

        if (pendingCount) {
            pendingCount.textContent = pending;
        }

        if (inactiveCount) {
            inactiveCount.textContent = inactive;
        }
    }


    function applyFilters() {

        const search =
            searchInput.value
                .trim()
                .toLowerCase();

        const college =
            collegeFilter.value;

        const status =
            statusFilter.value;

        let visibleCount = 0;


        rows.forEach(function (row) {

            const name =
                row.dataset.name || "";

            const email =
                row.dataset.email || "";

            const collegeName =
                row.dataset.college || "";

            const collegeId =
                row.dataset.collegeId || "";

            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                !search ||
                name.includes(search) ||
                email.includes(search) ||
                collegeName.includes(search);


            const matchesCollege =
                !college ||
                collegeId === college;


            const matchesStatus =
                !status ||
                rowStatus === status;


            const visible =
                matchesSearch &&
                matchesCollege &&
                matchesStatus;


            row.style.display =
                visible ? "" : "none";


            if (visible) {
                visibleCount++;
            }

        });


        if (resultCount) {
            resultCount.textContent =
                visibleCount;
        }

    }


    function resetAllFilters() {

        searchInput.value = "";
        collegeFilter.value = "";
        statusFilter.value = "";

        applyFilters();
    }


    if (searchInput) {
        searchInput.addEventListener(
            "input",
            applyFilters
        );
    }


    if (collegeFilter) {
        collegeFilter.addEventListener(
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


    if (resetFilters) {
        resetFilters.addEventListener(
            "click",
            resetAllFilters
        );
    }


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            function () {
                window.location.reload();
            }
        );

    }


    updateCounts();

});