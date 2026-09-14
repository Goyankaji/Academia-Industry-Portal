document.addEventListener("DOMContentLoaded", function () {

    const modal =
        document.getElementById("certificationModal");

    const form =
        document.getElementById("certificationForm");

    const modalTitle =
        document.getElementById("modalTitle");

    const closeButton =
        document.getElementById("closeCertificationModal");

    const cancelButton =
        document.getElementById("cancelCertification");

    const addButton =
        document.getElementById("openAddCertification");

    const emptyAddButton =
        document.getElementById("openAddCertificationEmpty");


    const certificateName =
        document.getElementById("certificate_name");

    const organization =
        document.getElementById("issuing_organization");

    const credential =
        document.getElementById("credential_id");

    const issueDate =
        document.getElementById("issue_date");

    const expiryDate =
        document.getElementById("expiry_date");

    const certificateUrl =
        document.getElementById("certificate_url");

    const description =
        document.getElementById("description");

    const certificateFile =
        document.getElementById("certificate_file");


    // =====================================================
    // OPEN ADD MODAL
    // =====================================================

    function openAddModal() {

        modalTitle.textContent =
            "Add Certification";

        form.action =
            "/student/certifications/add";

        form.reset();

        modal.hidden = false;

    }


    // =====================================================
    // CLOSE MODAL
    // =====================================================

    function closeModal() {

        modal.hidden = true;

    }


    // =====================================================
    // ADD BUTTONS
    // =====================================================

    if (addButton) {

        addButton.addEventListener(
            "click",
            openAddModal
        );

    }

    if (emptyAddButton) {

        emptyAddButton.addEventListener(
            "click",
            openAddModal
        );

    }


    // =====================================================
    // CLOSE BUTTONS
    // =====================================================

    closeButton.addEventListener(
        "click",
        closeModal
    );

    cancelButton.addEventListener(
        "click",
        closeModal
    );


    // =====================================================
    // CLICK OUTSIDE MODAL
    // =====================================================

    modal.addEventListener(
        "click",
        function (event) {

            if (
                event.target === modal
            ) {

                closeModal();

            }

        }
    );


    // =====================================================
    // EDIT CERTIFICATION
    // =====================================================

    document
        .querySelectorAll(".edit-certification")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const card =
                        button.closest(
                            ".certification-card"
                        );

                    const data =
                        card.querySelector(
                            ".certification-data"
                        );

                    const certificationId =
                        button.dataset.id;


                    modalTitle.textContent =
                        "Edit Certification";


                    form.action =
                        "/student/certifications/"
                        + certificationId
                        + "/update";


                    certificateName.value =
                        data.dataset.name || "";

                    organization.value =
                        data.dataset.organization || "";

                    credential.value =
                        data.dataset.credential || "";

                    issueDate.value =
                        data.dataset.issueDate || "";

                    expiryDate.value =
                        data.dataset.expiryDate || "";

                    certificateUrl.value =
                        data.dataset.url || "";

                    description.value =
                        data.dataset.description || "";

                    certificateFile.value =
                        "";


                    modal.hidden = false;

                }
            );

        });


    // =====================================================
    // DELETE CONFIRMATION
    // =====================================================

    document
        .querySelectorAll(
            ".delete-certification-form"
        )
        .forEach(function (deleteForm) {

            deleteForm.addEventListener(
                "submit",
                function (event) {

                    const confirmed =
                        confirm(
                            "Are you sure you want to delete this certification?"
                        );

                    if (!confirmed) {

                        event.preventDefault();

                    }

                }
            );

        });


    // =====================================================
    // DATE VALIDATION
    // =====================================================

    form.addEventListener(
        "submit",
        function (event) {

            if (
                issueDate.value &&
                expiryDate.value &&
                expiryDate.value < issueDate.value
            ) {

                event.preventDefault();

                alert(
                    "Expiry date cannot be before issue date."
                );

                return;

            }

        }
    );


    // =====================================================
    // ESC KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                !modal.hidden
            ) {

                closeModal();

            }

        }
    );

});