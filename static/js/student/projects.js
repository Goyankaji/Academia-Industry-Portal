document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ADD PROJECT MODAL
    // =====================================================

    const modal =
        document.getElementById("projectModal");

    const openButton =
        document.getElementById("openAddProject");

    const emptyOpenButton =
        document.getElementById("openAddProjectEmpty");

    const closeButton =
        document.getElementById("closeProjectModal");

    const cancelButton =
        document.getElementById("cancelProject");


    function openModal() {

        if (modal) {
            modal.hidden = false;
        }

    }


    function closeModal() {

        if (modal) {
            modal.hidden = true;
        }

    }


    if (openButton) {

        openButton.addEventListener(
            "click",
            openModal
        );

    }


    if (emptyOpenButton) {

        emptyOpenButton.addEventListener(
            "click",
            openModal
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
    // ESCAPE
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


    // =====================================================
    // DATE VALIDATION
    // =====================================================

    const projectForms =
        document.querySelectorAll(
            "form"
        );


    projectForms.forEach(
        function (form) {

            form.addEventListener(
                "submit",
                function (event) {

                    const startDate =
                        form.querySelector(
                            'input[name="start_date"]'
                        );

                    const endDate =
                        form.querySelector(
                            'input[name="end_date"]'
                        );


                    if (
                        startDate &&
                        endDate &&
                        startDate.value &&
                        endDate.value &&
                        endDate.value < startDate.value
                    ) {

                        event.preventDefault();

                        alert(
                            "End date cannot be before start date."
                        );

                    }

                }
            );

        }
    );


    // =====================================================
    // DELETE CONFIRMATION
    // =====================================================

    const deleteForm =
        document.getElementById(
            "deleteProjectForm"
        );


    if (deleteForm) {

        deleteForm.addEventListener(
            "submit",
            function (event) {

                const confirmed =
                    confirm(
                        "Are you sure you want to delete this project?"
                    );

                if (!confirmed) {

                    event.preventDefault();

                }

            }
        );

    }


    // =====================================================
    // EDIT PROJECT SECTION
    // =====================================================

    const editSection =
        document.getElementById(
            "editProjectSection"
        );

    const openEdit =
        document.getElementById(
            "openEditProject"
        );

    const closeEdit =
        document.getElementById(
            "closeEditProject"
        );


    if (openEdit && editSection) {

        openEdit.addEventListener(
            "click",
            function () {

                editSection.hidden = false;

                editSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }
        );

    }


    if (closeEdit && editSection) {

        closeEdit.addEventListener(
            "click",
            function () {

                editSection.hidden = true;

            }
        );

    }

});