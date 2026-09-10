document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".collaboration-form");
    const description = document.getElementById("description");
    const counter = document.getElementById("descriptionCounter");
    const startDate = document.getElementById("start_date");
    const endDate = document.getElementById("end_date");

    /* ==========================================
       DESCRIPTION CHARACTER COUNTER
       ========================================== */

    function updateDescriptionCounter() {
        if (!description || !counter) return;

        const currentLength = description.value.length;
        const maxLength = description.maxLength || 2000;

        counter.textContent = `${currentLength} / ${maxLength}`;

        if (currentLength >= maxLength) {
            counter.style.color = "#dc2626";
        } else if (currentLength >= maxLength * 0.9) {
            counter.style.color = "#d97706";
        } else {
            counter.style.color = "";
        }
    }

    if (description) {
        description.addEventListener("input", updateDescriptionCounter);
        updateDescriptionCounter();
    }


    /* ==========================================
       DATE VALIDATION
       ========================================== */

    function validateDates() {

        if (!startDate || !endDate) return true;

        if (
            startDate.value &&
            endDate.value &&
            endDate.value < startDate.value
        ) {
            endDate.setCustomValidity(
                "End date cannot be earlier than the start date."
            );

            return false;
        }

        endDate.setCustomValidity("");

        return true;
    }

    if (startDate) {
        startDate.addEventListener("change", function () {

            if (endDate && startDate.value) {
                endDate.min = startDate.value;
            }

            validateDates();
        });
    }

    if (endDate) {
        endDate.addEventListener("change", validateDates);
    }


    /* ==========================================
       FORM SUBMISSION
       ========================================== */

    if (form) {

        form.addEventListener("submit", function (event) {

            if (!validateDates()) {
                event.preventDefault();
                endDate.focus();
                return;
            }

            const submitButton = form.querySelector(
                ".submit-btn"
            );

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.innerHTML = `
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    Sending Request...
                `;
            }
        });
    }


    /* ==========================================
       INDUSTRY SELECT
       ========================================== */

    const industrySelect = document.getElementById("industry_id");

    if (industrySelect) {

        industrySelect.addEventListener("change", function () {

            if (this.value) {
                this.classList.add("has-value");
            } else {
                this.classList.remove("has-value");
            }

        });
    }

});