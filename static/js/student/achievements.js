document.addEventListener("DOMContentLoaded", function () {

    const modal =
        document.getElementById("achievementModal");

    const form =
        document.getElementById("achievementForm");

    const modalTitle =
        document.getElementById("modalTitle");

    const openButton =
        document.getElementById("openAddAchievement");

    const emptyOpenButton =
        document.getElementById(
            "openAddAchievementEmpty"
        );

    const closeButton =
        document.getElementById(
            "closeAchievementModal"
        );

    const cancelButton =
        document.getElementById(
            "cancelAchievement"
        );


    const title =
        document.getElementById(
            "achievementTitle"
        );

    const type =
        document.getElementById(
            "achievementType"
        );

    const date =
        document.getElementById(
            "achievementDate"
        );

    const organization =
        document.getElementById(
            "issuingOrganization"
        );

    const proof =
        document.getElementById(
            "proofUrl"
        );

    const description =
        document.getElementById(
            "achievementDescription"
        );


    // =====================================================
    // OPEN ADD MODAL
    // =====================================================

    function openAddModal() {

        modalTitle.textContent =
            "Add Achievement";

        form.action =
            "/student/achievements/add";

        form.reset();

        modal.hidden = false;

    }


    // =====================================================
    // CLOSE MODAL
    // =====================================================

    function closeModal() {

        modal.hidden = true;

    }


    if (openButton) {

        openButton.addEventListener(
            "click",
            openAddModal
        );

    }


    if (emptyOpenButton) {

        emptyOpenButton.addEventListener(
            "click",
            openAddModal
        );

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeModal
        );

    }


    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            closeModal
        );

    }


    // =====================================================
    // CLICK OUTSIDE
    // =====================================================

    if (modal) {

        modal.addEventListener(
            "click",
            function (event) {

                if (event.target === modal) {

                    closeModal();

                }

            }
        );

    }


    // =====================================================
    // EDIT
    // =====================================================

    document
        .querySelectorAll(
            ".edit-achievement"
        )
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const card =
                        button.closest(
                            ".achievement-card"
                        );

                    const data =
                        card.querySelector(
                            ".achievement-data"
                        );

                    const achievementId =
                        button.dataset.id;


                    modalTitle.textContent =
                        "Edit Achievement";


                    form.action =
                        "/student/achievements/"
                        + achievementId
                        + "/update";


                    title.value =
                        data.dataset.title || "";

                    type.value =
                        data.dataset.type || "";

                    date.value =
                        data.dataset.date || "";

                    organization.value =
                        data.dataset.organization || "";

                    proof.value =
                        data.dataset.proof || "";

                    description.value =
                        data.dataset.description || "";


                    modal.hidden = false;

                }
            );

        });


    // =====================================================
    // DELETE CONFIRMATION
    // =====================================================

    document
        .querySelectorAll(
            ".delete-achievement-form"
        )
        .forEach(function (deleteForm) {

            deleteForm.addEventListener(
                "submit",
                function (event) {

                    const confirmed =
                        confirm(
                            "Are you sure you want to delete this achievement?"
                        );

                    if (!confirmed) {

                        event.preventDefault();

                    }

                }
            );

        });


    // =====================================================
    // ESCAPE KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                !modal.hidden
            ) {

                closeModal();

            }

        }
    );

});