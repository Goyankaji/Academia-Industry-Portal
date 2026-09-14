document.addEventListener("DOMContentLoaded", function () {

    const statusFilter =
        document.getElementById("statusFilter");

    const applicationList =
        document.getElementById("applicationsList");

    if (statusFilter && applicationList) {

        const cards =
            applicationList.querySelectorAll(
                ".application-dashboard-card"
            );

        statusFilter.addEventListener("change", function () {

            const selectedStatus =
                statusFilter.value;

            cards.forEach(function (card) {

                const cardStatus =
                    card.dataset.status;

                if (
                    !selectedStatus ||
                    cardStatus === selectedStatus
                ) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }

            });

        });
    }


    const withdrawForms =
        document.querySelectorAll(".withdraw-form");

    withdrawForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed =
                confirm(
                    "Are you sure you want to withdraw this application?"
                );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});

/* =========================================================
   PHASE 4.4 - APPLICATION DETAIL
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const withdrawForm =
        document.getElementById("withdrawApplicationForm");

    if (withdrawForm) {

        withdrawForm.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to withdraw this application?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    }

});