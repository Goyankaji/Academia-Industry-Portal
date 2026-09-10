/* =========================================================
   STUDENT OPPORTUNITIES JS
   ========================================================= */


document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =================================================
           DATE FORMAT
           ================================================= */

        const deadlineElements =
            document.querySelectorAll(
                "[data-deadline]"
            );


        deadlineElements.forEach(
            function (element) {

                const rawDate =
                    element.dataset.deadline;


                if (
                    !rawDate ||
                    rawDate === "None"
                ) {

                    return;

                }


                const date =
                    new Date(rawDate);


                if (
                    Number.isNaN(
                        date.getTime()
                    )
                ) {

                    return;

                }


                element.textContent =
                    date.toLocaleDateString(
                        "en-IN",
                        {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        }
                    );

            }
        );



        /* =================================================
           SEARCH INPUT
           ================================================= */

        const searchInput =
            document.getElementById(
                "opportunitySearch"
            );


        if (searchInput) {

            searchInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();


                        if (
                            searchInput.form
                        ) {

                            searchInput.form.submit();

                        }

                    }

                }
            );

        }



        /* =================================================
           AUTO SUBMIT FILTERS
           ================================================= */

        const typeFilter =
            document.getElementById(
                "opportunityType"
            );


        const workModeFilter =
            document.getElementById(
                "workMode"
            );


        function submitFilters() {

            const form =
                document.getElementById(
                    "opportunityFilterForm"
                );


            if (form) {

                form.submit();

            }

        }


        if (typeFilter) {

            typeFilter.addEventListener(
                "change",
                submitFilters
            );

        }


        if (workModeFilter) {

            workModeFilter.addEventListener(
                "change",
                submitFilters
            );

        }



        /* =================================================
           DETAIL PAGE — APPLICATION FORM
           ================================================= */

        const openApplicationBtn =
            document.getElementById(
                "openApplicationBtn"
            );


        const cancelApplicationBtn =
            document.getElementById(
                "cancelApplicationBtn"
            );


        const applicationFormWrapper =
            document.getElementById(
                "applicationFormWrapper"
            );


        if (
            openApplicationBtn &&
            applicationFormWrapper
        ) {

            openApplicationBtn.addEventListener(
                "click",
                function () {

                    applicationFormWrapper.classList.add(
                        "visible"
                    );


                    openApplicationBtn.style.display =
                        "none";


                    applicationFormWrapper
                        .scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });

                }
            );

        }



        /* =================================================
           CANCEL APPLICATION
           ================================================= */

        if (
            cancelApplicationBtn &&
            applicationFormWrapper
        ) {

            cancelApplicationBtn.addEventListener(
                "click",
                function () {

                    applicationFormWrapper.classList.remove(
                        "visible"
                    );


                    if (openApplicationBtn) {

                        openApplicationBtn.style.display =
                            "";

                    }

                }
            );

        }



        /* =================================================
           COVER LETTER COUNTER
           ================================================= */

        const coverLetter =
            document.getElementById(
                "cover_letter"
            );


        const coverLetterCount =
            document.getElementById(
                "coverLetterCount"
            );


        function updateCoverLetterCount() {

            if (
                !coverLetter ||
                !coverLetterCount
            ) {

                return;

            }


            coverLetterCount.textContent =
                coverLetter.value.length;

        }


        if (coverLetter) {

            coverLetter.addEventListener(
                "input",
                updateCoverLetterCount
            );


            updateCoverLetterCount();

        }



        /* =================================================
           APPLICATION SUBMIT
           ================================================= */

        const applicationForm =
            document.getElementById(
                "studentApplicationForm"
            );


        const submitApplicationBtn =
            document.getElementById(
                "submitApplicationBtn"
            );


        if (applicationForm) {

            applicationForm.addEventListener(
                "submit",
                function () {

                    if (
                        submitApplicationBtn
                    ) {

                        submitApplicationBtn.disabled =
                            true;


                        submitApplicationBtn.textContent =
                            "Submitting...";

                    }

                }
            );

        }



        /* =================================================
           PREVENT DOUBLE CLICK
           ================================================= */

        const applyButtons =
            document.querySelectorAll(
                ".apply-btn"
            );


        applyButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        button.style.pointerEvents =
                            "none";

                    }
                );

            }
        );

    }
);