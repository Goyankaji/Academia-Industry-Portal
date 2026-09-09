document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("projectForm");
    const startDate = document.getElementById("start_date");
    const endDate = document.getElementById("end_date");

    if (!form) {
        return;
    }


    // Prevent invalid date range
    if (startDate && endDate) {

        startDate.addEventListener("change", function () {
            if (startDate.value) {
                endDate.min = startDate.value;
            }
        });

        endDate.addEventListener("change", function () {

            if (
                startDate.value &&
                endDate.value &&
                endDate.value < startDate.value
            ) {
                endDate.setCustomValidity(
                    "End date cannot be before start date."
                );
            } else {
                endDate.setCustomValidity("");
            }
        });
    }


    // Basic form validation
    form.addEventListener("submit", function (event) {

        const title = document.getElementById("title");
        const student = document.getElementById("student_id");

        if (!title.value.trim()) {
            event.preventDefault();
            title.focus();
            return;
        }

        if (!student.value) {
            event.preventDefault();
            student.focus();
            return;
        }

        if (
            startDate.value &&
            endDate.value &&
            endDate.value < startDate.value
        ) {
            event.preventDefault();
            endDate.setCustomValidity(
                "End date cannot be before start date."
            );
            endDate.reportValidity();
        }

    });

});