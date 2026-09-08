document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       COMMON MODAL HELPERS
    ===================================================== */

    function openModal(modal) {

        if (!modal) return;

        modal.style.display = "block";
        document.body.style.overflow = "hidden";
    }


    function closeModal(modal) {

        if (!modal) return;

        modal.style.display = "none";
        document.body.style.overflow = "";
    }


    /* =====================================================
       COLLEGE SEARCH
    ===================================================== */

    const collegeSearch =
        document.getElementById("collegeSearch");

    const collegeStateFilter =
        document.getElementById("collegeStateFilter");

    const collegeGrid =
        document.getElementById("collegeGrid");

    const collegeResultCount =
        document.getElementById("collegeResultCount");

    const collegeNoResults =
        document.getElementById("collegeNoResults");

    const clearCollegeFilters =
        document.getElementById("clearCollegeFilters");


    function filterColleges() {

        if (!collegeGrid) return;

        const cards =
            collegeGrid.querySelectorAll(
                ".industry-college-card"
            );

        const search =
            (collegeSearch?.value || "")
                .trim()
                .toLowerCase();

        const state =
            (collegeStateFilter?.value || "")
                .trim()
                .toLowerCase();

        let count = 0;


        cards.forEach(function (card) {

            const name =
                card.dataset.name || "";

            const university =
                card.dataset.university || "";

            const city =
                card.dataset.city || "";

            const cardState =
                card.dataset.state || "";


            const matchesSearch =
                !search ||
                name.includes(search) ||
                university.includes(search) ||
                city.includes(search) ||
                cardState.includes(search);


            const matchesState =
                !state ||
                cardState === state;


            const visible =
                matchesSearch &&
                matchesState;


            card.style.display =
                visible ? "" : "none";


            if (visible) {
                count++;
            }

        });


        if (collegeResultCount) {

            collegeResultCount.textContent =
                count +
                (count === 1
                    ? " college"
                    : " colleges");
        }


        if (collegeNoResults) {

            collegeNoResults.style.display =
                count === 0 ? "flex" : "none";
        }

    }


    if (collegeSearch) {

        collegeSearch.addEventListener(
            "input",
            filterColleges
        );

    }


    if (collegeStateFilter) {

        collegeStateFilter.addEventListener(
            "change",
            filterColleges
        );

    }


    if (clearCollegeFilters) {

        clearCollegeFilters.addEventListener(
            "click",
            function () {

                if (collegeSearch) {
                    collegeSearch.value = "";
                }

                if (collegeStateFilter) {
                    collegeStateFilter.value = "";
                }

                filterColleges();

            }
        );

    }


    filterColleges();


    /* =====================================================
       COLLEGE DETAIL - REQUEST MODAL
    ===================================================== */

    const requestButton =
        document.getElementById(
            "requestCollaborationBtn"
        );

    const requestModal =
        document.getElementById(
            "collaborationRequestModal"
        );

    const closeRequestModal =
        document.getElementById(
            "closeCollaborationModal"
        );

    const cancelRequest =
        document.getElementById(
            "cancelCollaborationRequest"
        );


    if (requestButton) {

        requestButton.addEventListener(
            "click",
            function () {

                openModal(requestModal);

            }
        );

    }


    if (closeRequestModal) {

        closeRequestModal.addEventListener(
            "click",
            function () {

                closeModal(requestModal);

            }
        );

    }


    if (cancelRequest) {

        cancelRequest.addEventListener(
            "click",
            function () {

                closeModal(requestModal);

            }
        );

    }


    if (requestModal) {

        const overlay =
            requestModal.querySelector(
                ".industry-modal-overlay"
            );

        if (overlay) {

            overlay.addEventListener(
                "click",
                function () {

                    closeModal(requestModal);

                }
            );

        }

    }


    /* =====================================================
       DESCRIPTION COUNTER
    ===================================================== */

    const description =
        document.getElementById(
            "collaborationDescription"
        );

    const descriptionCount =
        document.getElementById(
            "collaborationDescriptionCount"
        );


    if (description && descriptionCount) {

        function updateCounter() {

            descriptionCount.textContent =
                description.value.length;

        }


        description.addEventListener(
            "input",
            updateCounter
        );


        updateCounter();

    }


    /* =====================================================
       COLLABORATION SEARCH / FILTER
    ===================================================== */

    const collaborationSearch =
        document.getElementById(
            "collaborationSearch"
        );

    const collaborationStatusFilter =
        document.getElementById(
            "collaborationStatusFilter"
        );

    const collaborationTypeFilter =
        document.getElementById(
            "collaborationTypeFilter"
        );

    const collaborationList =
        document.getElementById(
            "collaborationRequestList"
        );

    const collaborationResultCount =
        document.getElementById(
            "collaborationResultCount"
        );

    const collaborationNoResults =
        document.getElementById(
            "collaborationNoResults"
        );

    const clearCollaborationFilters =
        document.getElementById(
            "clearCollaborationFilters"
        );


    function filterCollaborations() {

        if (!collaborationList) return;


        const cards =
            collaborationList.querySelectorAll(
                ".industry-collaboration-card"
            );


        const search =
            (collaborationSearch?.value || "")
                .trim()
                .toLowerCase();


        const status =
            (collaborationStatusFilter?.value || "")
                .trim()
                .toUpperCase();


        const type =
            (collaborationTypeFilter?.value || "")
                .trim()
                .toUpperCase();


        let count = 0;


        cards.forEach(function (card) {

            const title =
                (card.dataset.title || "")
                    .toLowerCase();

            const college =
                (card.dataset.college || "")
                    .toLowerCase();

            const cardStatus =
                (card.dataset.status || "")
                    .toUpperCase();

            const cardType =
                (card.dataset.type || "")
                    .toUpperCase();


            const matchesSearch =
                !search ||
                title.includes(search) ||
                college.includes(search);


            const matchesStatus =
                !status ||
                cardStatus === status;


            const matchesType =
                !type ||
                cardType === type;


            const visible =
                matchesSearch &&
                matchesStatus &&
                matchesType;


            card.style.display =
                visible ? "" : "none";


            if (visible) {
                count++;
            }

        });


        if (collaborationResultCount) {

            collaborationResultCount.textContent =
                count +
                (count === 1
                    ? " request"
                    : " requests");

        }


        if (collaborationNoResults) {

            collaborationNoResults.style.display =
                count === 0 ? "flex" : "none";

        }

    }


    if (collaborationSearch) {

        collaborationSearch.addEventListener(
            "input",
            filterCollaborations
        );

    }


    if (collaborationStatusFilter) {

        collaborationStatusFilter.addEventListener(
            "change",
            filterCollaborations
        );

    }


    if (collaborationTypeFilter) {

        collaborationTypeFilter.addEventListener(
            "change",
            filterCollaborations
        );

    }


    if (clearCollaborationFilters) {

        clearCollaborationFilters.addEventListener(
            "click",
            function () {

                if (collaborationSearch) {
                    collaborationSearch.value = "";
                }

                if (collaborationStatusFilter) {
                    collaborationStatusFilter.value = "";
                }

                if (collaborationTypeFilter) {
                    collaborationTypeFilter.value = "";
                }

                filterCollaborations();

            }
        );

    }


    filterCollaborations();


    /* =====================================================
       VIEW COLLABORATION DETAILS MODAL
    ===================================================== */

    const detailsModal =
        document.getElementById(
            "collaborationDetailsModal"
        );

    const closeDetailsModal =
        document.getElementById(
            "closeDetailsModal"
        );


    const detailTitle =
        document.getElementById(
            "detailModalTitle"
        );

    const detailCollege =
        document.getElementById(
            "detailModalCollege"
        );

    const detailType =
        document.getElementById(
            "detailModalType"
        );

    const detailStatus =
        document.getElementById(
            "detailModalStatus"
        );

    const detailDescription =
        document.getElementById(
            "detailModalDescription"
        );


    const viewButtons =
        document.querySelectorAll(
            ".collaboration-view-btn"
        );


    viewButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                if (detailTitle) {
                    detailTitle.textContent =
                        button.dataset.title || "Collaboration";
                }

                if (detailCollege) {
                    detailCollege.textContent =
                        button.dataset.college || "—";
                }

                if (detailType) {
                    detailType.textContent =
                        (button.dataset.type || "—")
                            .replaceAll("_", " ");
                }

                if (detailStatus) {
                    detailStatus.textContent =
                        button.dataset.status || "—";
                }

                if (detailDescription) {
                    detailDescription.textContent =
                        button.dataset.description || "No description provided.";
                }

                openModal(detailsModal);

            }
        );

    });


    if (closeDetailsModal) {

        closeDetailsModal.addEventListener(
            "click",
            function () {

                closeModal(detailsModal);

            }
        );

    }


    if (detailsModal) {

        const overlay =
            detailsModal.querySelector(
                ".industry-modal-overlay"
            );

        if (overlay) {

            overlay.addEventListener(
                "click",
                function () {

                    closeModal(detailsModal);

                }
            );

        }

    }


    /* =====================================================
       CANCEL COLLABORATION
    ===================================================== */

    const cancelButtons =
        document.querySelectorAll(
            ".collaboration-cancel-btn"
        );

    const cancelModal =
        document.getElementById(
            "cancelCollaborationModal"
        );

    const closeCancelModal =
        document.getElementById(
            "closeCancelCollaborationModal"
        );

    const keepRequest =
        document.getElementById(
            "keepCollaborationRequest"
        );

    const confirmCancel =
        document.getElementById(
            "confirmCancelCollaboration"
        );


    let selectedCollaborationId = null;


    cancelButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                selectedCollaborationId =
                    button.dataset.collaborationId;

                openModal(cancelModal);

            }
        );

    });


    if (closeCancelModal) {

        closeCancelModal.addEventListener(
            "click",
            function () {

                closeModal(cancelModal);

            }
        );

    }


    if (keepRequest) {

        keepRequest.addEventListener(
            "click",
            function () {

                closeModal(cancelModal);

            }
        );

    }


    if (confirmCancel) {

        confirmCancel.addEventListener(
            "click",
            function () {

                if (!selectedCollaborationId) {

                    alert(
                        "Collaboration ID not found."
                    );

                    return;
                }


                const form =
                    document.createElement("form");

                form.method = "POST";

                form.action =
                    `/industry/collaboration/${selectedCollaborationId}/cancel`;

                document.body.appendChild(form);

                form.submit();

            }
        );

    }


    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key !== "Escape") {
                return;
            }

            closeModal(requestModal);
            closeModal(detailsModal);
            closeModal(cancelModal);

        }
    );

});