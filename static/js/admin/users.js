/* =========================================================
   SIH ADMIN PORTAL
   USERS MANAGEMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    const searchInput =
        document.getElementById("userSearch");

    const roleFilter =
        document.getElementById("roleFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const resetFilters =
        document.getElementById("resetFilters");

    const refreshButton =
        document.getElementById("refreshUsers");

    const visibleCount =
        document.getElementById("visibleUserCount");

    const activeCount =
        document.getElementById("activeUserCount");

    const inactiveCount =
        document.getElementById("inactiveUserCount");

    const filterEmptyRow =
        document.getElementById("filterEmptyRow");

    const userRows =
        document.querySelectorAll(".user-row");


    /* =====================================================
       UPDATE STATISTICS
       ===================================================== */

    function updateCounts() {

        let active = 0;
        let inactive = 0;


        userRows.forEach(function (row) {

            const status =
                row.dataset.status || "";


            if (status === "ACTIVE") {

                active++;

            }


            if (status === "INACTIVE") {

                inactive++;

            }

        });


        if (activeCount) {

            activeCount.textContent =
                active;

        }


        if (inactiveCount) {

            inactiveCount.textContent =
                inactive;

        }

    }


    /* =====================================================
       FILTER USERS
       ===================================================== */

    function filterUsers() {

        const search =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const role =
            roleFilter
                ? roleFilter.value
                : "";


        const status =
            statusFilter
                ? statusFilter.value
                : "";


        let visibleUsers = 0;


        userRows.forEach(function (row) {

            const name =
                row.dataset.name || "";

            const email =
                row.dataset.email || "";

            const rowRole =
                row.dataset.role || "";

            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                !search ||
                name.includes(search) ||
                email.includes(search);


            const matchesRole =
                !role ||
                rowRole === role;


            const matchesStatus =
                !status ||
                rowStatus === status;


            const shouldShow =
                matchesSearch &&
                matchesRole &&
                matchesStatus;


            if (shouldShow) {

                row.classList.remove("hidden");

                visibleUsers++;

            }

            else {

                row.classList.add("hidden");

            }

        });


        if (visibleCount) {

            visibleCount.textContent =
                visibleUsers;

        }


        if (filterEmptyRow) {

            if (
                visibleUsers === 0 &&
                userRows.length > 0
            ) {

                filterEmptyRow.classList.remove(
                    "hidden"
                );

            }

            else {

                filterEmptyRow.classList.add(
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
            filterUsers
        );

    }


    if (roleFilter) {

        roleFilter.addEventListener(
            "change",
            filterUsers
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterUsers
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

                if (roleFilter) {

                    roleFilter.value = "";

                }

                if (statusFilter) {

                    statusFilter.value = "";

                }

                filterUsers();

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

    filterUsers();


    console.log(
        "SIH Admin Users JS loaded successfully."
    );

});