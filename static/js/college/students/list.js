document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("studentSearch");
    const departmentFilter = document.getElementById("departmentFilter");
    const statusFilter = document.getElementById("statusFilter");

    const rows = document.querySelectorAll(".student-row");
    const filterEmpty = document.getElementById("filterEmpty");
    const resultCount = document.getElementById("resultCount");

    function filterStudents() {

        const search = searchInput.value.trim().toLowerCase();
        const department = departmentFilter.value.toLowerCase();
        const status = statusFilter.value.toLowerCase();

        let visibleCount = 0;

        rows.forEach(function (row) {

            const name = row.dataset.name || "";
            const enrollment = row.dataset.enrollment || "";
            const email = row.dataset.email || "";
            const branch = row.dataset.branch || "";
            const rowDepartment = row.dataset.department || "";
            const rowStatus = row.dataset.status || "";

            const matchesSearch =
                !search ||
                name.includes(search) ||
                enrollment.includes(search) ||
                email.includes(search) ||
                branch.includes(search);

            const matchesDepartment =
                department === "all" ||
                rowDepartment === department;

            const matchesStatus =
                status === "all" ||
                rowStatus === status;

            if (
                matchesSearch &&
                matchesDepartment &&
                matchesStatus
            ) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }

        });

        resultCount.textContent =
            visibleCount +
            (visibleCount === 1 ? " Student" : " Students");

        if (filterEmpty) {
            filterEmpty.style.display =
                visibleCount === 0 ? "block" : "none";
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", filterStudents);
    }

    if (departmentFilter) {
        departmentFilter.addEventListener("change", filterStudents);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", filterStudents);
    }

});