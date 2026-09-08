/* =========================================================
   INDUSTRY REQUIREMENTS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       SEARCH + FILTER
    ====================================================== */

    const searchInput =
        document.getElementById("requirementSearch");

    const typeFilter =
        document.getElementById("requirementTypeFilter");

    const statusFilter =
        document.getElementById("requirementStatusFilter");

    const cards =
        document.querySelectorAll(
            ".industry-requirement-card"
        );

    const noResults =
        document.getElementById(
            "noRequirementResults"
        );


    function filterRequirements() {

        if (!cards.length) {
            return;
        }


        const searchValue =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const typeValue =
            typeFilter
                ? typeFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        const statusValue =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toUpperCase()
                : "";


        let visibleCount = 0;


        cards.forEach(function (card) {

            const title =
                card.dataset.title || "";

            const type =
                card.dataset.type || "";

            const status =
                card.dataset.status || "";


            const matchesSearch =
                !searchValue ||
                title.includes(searchValue);


            const matchesType =
                !typeValue ||
                type === typeValue;


            const matchesStatus =
                !statusValue ||
                status === statusValue;


            const shouldShow =
                matchesSearch &&
                matchesType &&
                matchesStatus;


            if (shouldShow) {

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
            filterRequirements
        );

    }


    if (typeFilter) {

        typeFilter.addEventListener(
            "change",
            filterRequirements
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterRequirements
        );

    }


    /* =====================================================
       DESCRIPTION CHARACTER COUNTER
    ====================================================== */

    const description =
        document.getElementById(
            "description"
        );

    const descriptionCounter =
        document.getElementById(
            "descriptionCounter"
        );


    function updateDescriptionCounter() {

        if (!description ||
            !descriptionCounter) {

            return;

        }


        const length =
            description.value.length;


        descriptionCounter.textContent =
            length + " / 3000";

    }


    if (description) {

        description.addEventListener(
            "input",
            updateDescriptionCounter
        );


        updateDescriptionCounter();

    }


    /* =====================================================
       CREATE / EDIT FORM VALIDATION
    ====================================================== */

    const createForm =
        document.getElementById(
            "createRequirementForm"
        );

    const editForm =
        document.getElementById(
            "editRequirementForm"
        );


    function validateRequirementForm(
        form
    ) {

        if (!form) {
            return true;
        }


        const title =
            form.querySelector(
                '[name="title"]'
            );


        const opportunityType =
            form.querySelector(
                '[name="opportunity_type"]'
            );


        const descriptionField =
            form.querySelector(
                '[name="description"]'
            );


        if (title &&
            title.value.trim().length < 3) {

            alert(
                "Requirement title must contain at least 3 characters."
            );

            title.focus();

            return false;

        }


        if (opportunityType &&
            !opportunityType.value) {

            alert(
                "Please select an opportunity type."
            );

            opportunityType.focus();

            return false;

        }


        if (descriptionField &&
            descriptionField.value.trim().length < 10) {

            alert(
                "Description must contain at least 10 characters."
            );

            descriptionField.focus();

            return false;

        }


        return true;

    }


    if (createForm) {

        createForm.addEventListener(
            "submit",
            function (event) {

                if (!validateRequirementForm(
                    createForm
                )) {

                    event.preventDefault();

                    return;

                }


                const submitButton =
                    createForm.querySelector(
                        'button[type="submit"]'
                    );


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.innerHTML =
                        "Creating...";

                }

            }
        );

    }


    if (editForm) {

        editForm.addEventListener(
            "submit",
            function (event) {

                if (!validateRequirementForm(
                    editForm
                )) {

                    event.preventDefault();

                    return;

                }


                const submitButton =
                    editForm.querySelector(
                        'button[type="submit"]'
                    );


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.innerHTML =
                        "Saving...";

                }

            }
        );

    }


    /* =====================================================
       CLOSE REQUIREMENT MODAL
    ====================================================== */

    const closeButton =
        document.getElementById(
            "closeRequirementBtn"
        );

    const modal =
        document.getElementById(
            "closeRequirementModal"
        );

    const cancelCloseButton =
        document.getElementById(
            "cancelCloseRequirement"
        );

    const confirmCloseButton =
        document.getElementById(
            "confirmCloseRequirement"
        );


    function openCloseModal() {

        if (!modal) {
            return;
        }

        modal.classList.remove(
            "hidden"
        );

        document.body.style.overflow =
            "hidden";

    }


    function closeCloseModal() {

        if (!modal) {
            return;
        }

        modal.classList.add(
            "hidden"
        );

        document.body.style.overflow =
            "";

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            openCloseModal
        );

    }


    if (cancelCloseButton) {

        cancelCloseButton.addEventListener(
            "click",
            closeCloseModal
        );

    }


    /* =====================================================
       CLOSE MODAL ON OVERLAY CLICK
    ====================================================== */

    const modalOverlay =
        document.querySelector(
            ".requirement-modal-overlay"
        );


    if (modalOverlay) {

        modalOverlay.addEventListener(
            "click",
            closeCloseModal
        );

    }


    /* =====================================================
       CONFIRM CLOSE
    ====================================================== */

    if (confirmCloseButton) {

        confirmCloseButton.addEventListener(
            "click",
            function () {


                const requirementId =
                    closeButton &&
                    closeButton.dataset
                        ? closeButton.dataset.requirementId
                        : null;


                if (!requirementId) {

                    alert(
                        "Requirement ID not found."
                    );

                    return;

                }


                confirmCloseButton.disabled =
                    true;


                confirmCloseButton.textContent =
                    "Closing...";


                /*
                 * Backend endpoint:
                 *
                 * POST
                 * /industry/requirements/<id>/close
                 *
                 */

                const form =
                    document.createElement(
                        "form"
                    );


                form.method = "POST";


                form.action =
                    "/industry/requirements/" +
                    encodeURIComponent(
                        requirementId
                    ) +
                    "/close";


                document.body.appendChild(
                    form
                );


                form.submit();

            }
        );

    }


    /* =====================================================
       ESC KEY - CLOSE MODAL
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                !modal.classList.contains(
                    "hidden"
                )
            ) {

                closeCloseModal();

            }

        }
    );

});