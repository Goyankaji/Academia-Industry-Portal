document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const modal =
        document.getElementById("skillModal");

    const openAddBtn =
        document.getElementById("openAddSkillBtn");

    const openEmptyBtn =
        document.getElementById("openEmptyAddSkillBtn");

    const closeBtn =
        document.getElementById("closeSkillModalBtn");

    const cancelBtn =
        document.getElementById("cancelSkillBtn");

    const form =
        document.getElementById("skillForm");

    const modalTitle =
        document.getElementById("skillModalTitle");

    const modalSubtitle =
        document.getElementById("skillModalSubtitle");

    const skillName =
        document.getElementById("skill_name");

    const proficiency =
        document.getElementById("proficiency_level");

    const assessment =
        document.getElementById("assessment_percentage");

    const saveBtn =
        document.getElementById("saveSkillBtn");

    const saveText =
        document.getElementById("saveSkillText");


    /* =====================================================
       OPEN MODAL
       ===================================================== */

    function openModal() {

        if (!modal) {
            return;
        }

        modal.classList.add("active");

        document.body.style.overflow = "hidden";
    }


    /* =====================================================
       CLOSE MODAL
       ===================================================== */

    function closeModal() {

        if (!modal) {
            return;
        }

        modal.classList.remove("active");

        document.body.style.overflow = "";
    }


    /* =====================================================
       ADD MODE
       ===================================================== */

    function openAddMode() {

        if (!form) {
            return;
        }

        form.action = "/student/skills/add";

        if (modalTitle) {
            modalTitle.textContent = "Add Skill";
        }

        if (modalSubtitle) {
            modalSubtitle.textContent =
                "Add a skill to your student profile.";
        }

        if (skillName) {
            skillName.value = "";
        }

        if (proficiency) {
            proficiency.value = "";
        }

        if (assessment) {
            assessment.value = "0";
        }

        if (saveText) {
            saveText.textContent = "Save Skill";
        }

        openModal();

        setTimeout(function () {

            if (skillName) {
                skillName.focus();
            }

        }, 100);
    }


    /* =====================================================
       EDIT MODE
       ===================================================== */

    function openEditMode(button) {

        if (!button || !form) {
            return;
        }

        const id =
            button.dataset.id;

        const name =
            button.dataset.name || "";

        const level =
            button.dataset.level || "";

        const percentage =
            button.dataset.percentage || "0";


        form.action =
            "/student/skills/" +
            id +
            "/update";


        if (modalTitle) {
            modalTitle.textContent = "Edit Skill";
        }

        if (modalSubtitle) {
            modalSubtitle.textContent =
                "Update your skill information.";
        }


        if (skillName) {
            skillName.value = name;
        }

        if (proficiency) {
            proficiency.value = level;
        }

        if (assessment) {
            assessment.value = percentage;
        }


        if (saveText) {
            saveText.textContent = "Update Skill";
        }


        openModal();


        setTimeout(function () {

            if (skillName) {
                skillName.focus();
            }

        }, 100);
    }


    /* =====================================================
       ADD BUTTON
       ===================================================== */

    if (openAddBtn) {

        openAddBtn.addEventListener(
            "click",
            openAddMode
        );

    }


    /* =====================================================
       EMPTY STATE ADD BUTTON
       ===================================================== */

    if (openEmptyBtn) {

        openEmptyBtn.addEventListener(
            "click",
            openAddMode
        );

    }


    /* =====================================================
       CLOSE BUTTON
       ===================================================== */

    if (closeBtn) {

        closeBtn.addEventListener(
            "click",
            closeModal
        );

    }


    /* =====================================================
       CANCEL BUTTON
       ===================================================== */

    if (cancelBtn) {

        cancelBtn.addEventListener(
            "click",
            closeModal
        );

    }


    /* =====================================================
       CLICK OUTSIDE MODAL
       ===================================================== */

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


    /* =====================================================
       ESCAPE KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                modal.classList.contains("active")
            ) {

                closeModal();

            }

        }
    );


    /* =====================================================
       EDIT SKILL BUTTONS
       ===================================================== */

    const editButtons =
        document.querySelectorAll(
            ".edit-skill-btn"
        );


    editButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    openEditMode(button);

                }
            );

        }
    );


    /* =====================================================
       DELETE CONFIRMATION
       ===================================================== */

    const deleteForms =
        document.querySelectorAll(
            ".delete-skill-form"
        );


    deleteForms.forEach(
        function (deleteForm) {

            deleteForm.addEventListener(
                "submit",
                function (event) {

                    const confirmed =
                        window.confirm(
                            "Are you sure you want to delete this skill?"
                        );


                    if (!confirmed) {

                        event.preventDefault();

                    }

                }
            );

        }
    );


    /* =====================================================
       SKILL PROGRESS BARS
       ===================================================== */

    const progressBars =
        document.querySelectorAll(
            ".skill-progress-bar"
        );


    progressBars.forEach(
        function (bar) {

            const progress =
                parseFloat(
                    bar.dataset.progress
                ) || 0;


            const safeProgress =
                Math.max(
                    0,
                    Math.min(
                        100,
                        progress
                    )
                );


            bar.style.width =
                safeProgress + "%";

        }
    );


    /* =====================================================
       FORM VALIDATION
       ===================================================== */

    if (form) {

        form.addEventListener(
            "submit",
            function (event) {


                const name =
                    skillName
                        ? skillName.value.trim()
                        : "";


                const level =
                    proficiency
                        ? proficiency.value
                        : "";


                const percentage =
                    assessment
                        ? parseFloat(assessment.value)
                        : 0;


                /* -----------------------------------------
                   SKILL NAME
                   ----------------------------------------- */

                if (!name) {

                    event.preventDefault();

                    alert(
                        "Please enter a skill name."
                    );

                    if (skillName) {
                        skillName.focus();
                    }

                    return;
                }


                /* -----------------------------------------
                   PROFICIENCY
                   ----------------------------------------- */

                if (!level) {

                    event.preventDefault();

                    alert(
                        "Please select a proficiency level."
                    );

                    if (proficiency) {
                        proficiency.focus();
                    }

                    return;
                }


                /* -----------------------------------------
                   ASSESSMENT PERCENTAGE
                   ----------------------------------------- */

                if (
                    Number.isNaN(percentage) ||
                    percentage < 0 ||
                    percentage > 100
                ) {

                    event.preventDefault();

                    alert(
                        "Assessment percentage must be between 0 and 100."
                    );

                    if (assessment) {
                        assessment.focus();
                    }

                    return;
                }


                /* -----------------------------------------
                   PREVENT DOUBLE SUBMISSION
                   ----------------------------------------- */

                if (saveBtn) {

                    saveBtn.disabled = true;

                }

            }
        );

    }


    /* =====================================================
       AUTO HIDE FLASH MESSAGES
       ===================================================== */

    const flashMessages =
        document.querySelectorAll(
            ".skills-flash-message"
        );


    flashMessages.forEach(
        function (message) {

            setTimeout(
                function () {

                    message.style.opacity = "0";

                    message.style.transform =
                        "translateY(-4px)";

                    message.style.transition =
                        "all 0.25s ease";


                    setTimeout(
                        function () {

                            message.remove();

                        },
                        250
                    );

                },
                4500
            );

        }
    );

});