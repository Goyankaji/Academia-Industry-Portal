/* =========================================================
   INDUSTRY APPLICATIONS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       APPLICATION SEARCH + FILTER
    ====================================================== */

    const searchInput =
        document.getElementById("applicationSearch");

    const statusFilter =
        document.getElementById(
            "applicationStatusFilter"
        );

    const opportunityFilter =
        document.getElementById(
            "applicationOpportunityFilter"
        );

    const applicationCards =
        document.querySelectorAll(
            ".industry-application-card"
        );

    const noResults =
        document.getElementById(
            "noApplicationResults"
        );


    function filterApplications() {

        if (!applicationCards.length) {
            return;
        }


        const searchValue =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const statusValue =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        const opportunityValue =
            opportunityFilter
                ? opportunityFilter.value
                : "";


        let visibleCount = 0;


        applicationCards.forEach(function (card) {


            const student =
                card.dataset.student || "";


            const opportunity =
                card.dataset.opportunity || "";


            const status =
                card.dataset.status || "";


            const opportunityId =
                card.dataset.opportunityId || "";


            const matchesSearch =
                !searchValue ||
                student.includes(searchValue) ||
                opportunity.includes(searchValue);


            const matchesStatus =
                !statusValue ||
                status === statusValue;


            const matchesOpportunity =
                !opportunityValue ||
                opportunityId === opportunityValue;


            const visible =
                matchesSearch &&
                matchesStatus &&
                matchesOpportunity;


            if (visible) {

                card.style.display = "";

                visibleCount++;

            } else {

                card.style.display = "none";

            }

        });


        if (noResults) {

            if (visibleCount === 0) {

                noResults.classList.remove(
                    "hidden"
                );

            } else {

                noResults.classList.add(
                    "hidden"
                );

            }

        }

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterApplications
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterApplications
        );

    }


    if (opportunityFilter) {

        opportunityFilter.addEventListener(
            "change",
            filterApplications
        );

    }


    /* =====================================================
       APPLICATION STATUS BUTTONS
    ====================================================== */

    const statusButtons =
        document.querySelectorAll(
            ".application-status-button"
        );


    statusButtons.forEach(function (button) {


        button.addEventListener(
            "click",
            function () {


                const status =
                    button.dataset.status;


                const applicationId =
                    window.INDUSTRY_APPLICATION_ID;


                if (!applicationId) {

                    alert(
                        "Application ID not found."
                    );

                    return;

                }


                if (!status) {

                    alert(
                        "Application status not found."
                    );

                    return;

                }


                let message =
                    "Are you sure you want to mark this application as " +
                    status +
                    "?";


                if (!window.confirm(message)) {
                    return;
                }


                button.disabled = true;

                button.textContent =
                    "Updating...";


                /*
                 * Backend endpoint to be connected:
                 *
                 * POST
                 * /industry/applications/<id>/status
                 *
                 */


                const form =
                    document.createElement(
                        "form"
                    );


                form.method = "POST";


                form.action =
                    "/industry/applications/" +
                    encodeURIComponent(
                        applicationId
                    ) +
                    "/status";


                const statusInput =
                    document.createElement(
                        "input"
                    );


                statusInput.type =
                    "hidden";


                statusInput.name =
                    "status";


                statusInput.value =
                    status;


                form.appendChild(
                    statusInput
                );


                document.body.appendChild(
                    form
                );


                form.submit();

            }
        );

    });


});