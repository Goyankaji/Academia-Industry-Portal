document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("projectForm");
    const startDate = document.getElementById("start_date");
    const endDate = document.getElementById("end_date");

    if (!form) {
        return;
    }


    function validateDates() {

        if (
            startDate &&
            endDate &&
            startDate.value &&
            endDate.value
        ) {

            if (endDate.value < startDate.value) {

                endDate.setCustomValidity(
                    "End date cannot be before start date."
                );

                return false;
            }
        }

        if (endDate) {
            endDate.setCustomValidity("");
        }

        return true;
    }


    if (startDate && endDate) {

        startDate.addEventListener("change", function () {

            if (startDate.value) {
                endDate.min = startDate.value;
            }

            validateDates();
        });

        endDate.addEventListener("change", validateDates);
    }


    form.addEventListener("submit", function (event) {

        if (!validateDates()) {
            event.preventDefault();
            endDate.reportValidity();
        }

    });

});