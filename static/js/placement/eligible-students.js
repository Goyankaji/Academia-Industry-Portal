document.addEventListener("DOMContentLoaded", function () {

    // Search eligible students
    const searchInput = document.getElementById("studentSearch");
    const studentRows = document.querySelectorAll(".student-row");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const searchValue = this.value.toLowerCase().trim();

            studentRows.forEach(row => {
                const rowText = row.textContent.toLowerCase();

                if (rowText.includes(searchValue)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }

    // Filter by application status
    const statusFilter = document.getElementById("statusFilter");

    if (statusFilter) {
        statusFilter.addEventListener("change", function () {
            const selectedStatus = this.value.toLowerCase();

            studentRows.forEach(row => {
                const status = row.getAttribute("data-status");

                if (
                    selectedStatus === "" ||
                    (status && status.toLowerCase() === selectedStatus)
                ) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }

    // Combined search + status filtering
    function applyFilters() {
        const searchValue = searchInput
            ? searchInput.value.toLowerCase().trim()
            : "";

        const selectedStatus = statusFilter
            ? statusFilter.value.toLowerCase()
            : "";

        studentRows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            const status = (row.getAttribute("data-status") || "").toLowerCase();

            const matchesSearch =
                searchValue === "" || rowText.includes(searchValue);

            const matchesStatus =
                selectedStatus === "" || status === selectedStatus;

            row.style.display =
                matchesSearch && matchesStatus ? "" : "none";
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", applyFilters);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", applyFilters);
    }

    // Eligible student count after filtering
    const visibleCount = document.getElementById("visibleStudentCount");

    function updateVisibleCount() {
        if (!visibleCount) {
            return;
        }

        let count = 0;

        studentRows.forEach(row => {
            if (row.style.display !== "none") {
                count++;
            }
        });

        visibleCount.textContent = count;
    }

    if (searchInput || statusFilter) {
        document.addEventListener("input", updateVisibleCount);
        document.addEventListener("change", updateVisibleCount);
    }

});