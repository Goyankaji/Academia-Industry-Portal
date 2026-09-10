/* =========================================================
   STUDENT PROFILE JS
   ========================================================= */


document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =================================================
           PROFILE COMPLETION PROGRESS
           ================================================= */

        const profileProgress =
            document.querySelector(
                ".profile-progress-fill"
            );


        if (profileProgress) {

            let progress =
                parseInt(
                    profileProgress.dataset.progress,
                    10
                );


            if (isNaN(progress)) {

                progress = 0;

            }


            progress =
                Math.max(
                    0,
                    Math.min(
                        100,
                        progress
                    )
                );


            profileProgress.style.width =
                "0%";


            setTimeout(
                function () {

                    profileProgress.style.width =
                        progress + "%";

                },
                150
            );

        }



        /* =================================================
           SKILL PROGRESS BARS
           ================================================= */

        const skillProgressBars =
            document.querySelectorAll(
                ".skill-progress div[data-progress]"
            );


        skillProgressBars.forEach(
            function (bar) {

                let progress =
                    parseInt(
                        bar.dataset.progress,
                        10
                    );


                if (isNaN(progress)) {

                    progress = 0;

                }


                progress =
                    Math.max(
                        0,
                        Math.min(
                            100,
                            progress
                        )
                    );


                bar.style.width =
                    "0%";


                setTimeout(
                    function () {

                        bar.style.width =
                            progress + "%";

                    },
                    150
                );

            }
        );



        /* =================================================
           EDIT PROFILE FORM
           ================================================= */

        const form =
            document.getElementById(
                "studentProfileForm"
            );


        if (!form) {

            return;

        }



        /* =================================================
           FORM ELEMENTS
           ================================================= */

        const nameInput =
            document.getElementById(
                "name"
            );


        const semesterInput =
            document.getElementById(
                "semester"
            );


        const passingYearInput =
            document.getElementById(
                "passing_year"
            );


        const cgpaInput =
            document.getElementById(
                "cgpa"
            );


        const backlogInput =
            document.getElementById(
                "active_backlogs"
            );


        const phoneInput =
            document.getElementById(
                "phone"
            );


        const linkedinInput =
            document.getElementById(
                "linkedin_url"
            );


        const githubInput =
            document.getElementById(
                "github_url"
            );


        const portfolioInput =
            document.getElementById(
                "portfolio_url"
            );


        const saveButton =
            document.getElementById(
                "saveProfileBtn"
            );



        /* =================================================
           ERROR HELPERS
           ================================================= */

        function clearErrors() {

            document
                .querySelectorAll(
                    ".field-error"
                )
                .forEach(
                    function (element) {

                        element.textContent = "";

                    }
                );

        }


        function setError(
            input,
            message
        ) {

            if (!input) {

                return;

            }


            const parent =
                input.closest(
                    ".form-group"
                );


            if (!parent) {

                return;

            }


            const error =
                parent.querySelector(
                    ".field-error"
                );


            if (error) {

                error.textContent =
                    message;

            }


            input.focus();

        }



        /* =================================================
           URL VALIDATION
           ================================================= */

        function isValidUrl(value) {

            if (!value) {

                return true;

            }


            try {

                const url =
                    new URL(value);


                return (
                    url.protocol === "http:" ||
                    url.protocol === "https:"
                );

            } catch (error) {

                return false;

            }

        }



        /* =================================================
           PHONE VALIDATION
           ================================================= */

        function isValidPhone(value) {

            if (!value) {

                return true;

            }


            /*
             * Allows:
             * digits
             * spaces
             * +
             * -
             * brackets
             */

            return /^[0-9+\-\s()]{7,20}$/
                .test(value);

        }



        /* =================================================
           FORM SUBMIT
           ================================================= */

        form.addEventListener(
            "submit",
            function (event) {

                clearErrors();


                let valid = true;



                /* =========================================
                   NAME
                   ========================================= */

                if (
                    !nameInput ||
                    !nameInput.value.trim()
                ) {

                    setError(
                        nameInput,
                        "Name is required."
                    );

                    valid = false;

                }



                /* =========================================
                   PHONE
                   ========================================= */

                if (
                    valid &&
                    phoneInput &&
                    phoneInput.value.trim()
                ) {

                    if (
                        !isValidPhone(
                            phoneInput.value.trim()
                        )
                    ) {

                        setError(
                            phoneInput,
                            "Please enter a valid phone number."
                        );

                        valid = false;

                    }

                }



                /* =========================================
                   SEMESTER
                   ========================================= */

                if (
                    valid &&
                    semesterInput &&
                    semesterInput.value
                ) {

                    const semester =
                        Number(
                            semesterInput.value
                        );


                    if (
                        !Number.isInteger(
                            semester
                        ) ||
                        semester < 1 ||
                        semester > 12
                    ) {

                        setError(
                            semesterInput,
                            "Semester must be between 1 and 12."
                        );

                        valid = false;

                    }

                }



                /* =========================================
                   PASSING YEAR
                   ========================================= */

                if (
                    valid &&
                    passingYearInput &&
                    passingYearInput.value
                ) {

                    const year =
                        Number(
                            passingYearInput.value
                        );


                    if (
                        !Number.isInteger(
                            year
                        ) ||
                        year < 2000 ||
                        year > 2100
                    ) {

                        setError(
                            passingYearInput,
                            "Please enter a valid passing year."
                        );

                        valid = false;

                    }

                }



                /* =========================================
                   CGPA
                   ========================================= */

                if (
                    valid &&
                    cgpaInput &&
                    cgpaInput.value
                ) {

                    const cgpa =
                        Number(
                            cgpaInput.value
                        );


                    if (
                        isNaN(cgpa) ||
                        cgpa < 0 ||
                        cgpa > 10
                    ) {

                        setError(
                            cgpaInput,
                            "CGPA must be between 0 and 10."
                        );

                        valid = false;

                    }

                }



                /* =========================================
                   ACTIVE BACKLOGS
                   ========================================= */

                if (
                    valid &&
                    backlogInput &&
                    backlogInput.value
                ) {

                    const backlogs =
                        Number(
                            backlogInput.value
                        );


                    if (
                        !Number.isInteger(
                            backlogs
                        ) ||
                        backlogs < 0
                    ) {

                        setError(
                            backlogInput,
                            "Backlogs cannot be negative."
                        );

                        valid = false;

                    }

                }



                /* =========================================
                   LINKEDIN
                   ========================================= */

                if (
                    valid &&
                    linkedinInput &&
                    !isValidUrl(
                        linkedinInput.value.trim()
                    )
                ) {

                    setError(
                        linkedinInput,
                        "Please enter a valid LinkedIn URL."
                    );

                    valid = false;

                }



                /* =========================================
                   GITHUB
                   ========================================= */

                if (
                    valid &&
                    githubInput &&
                    !isValidUrl(
                        githubInput.value.trim()
                    )
                ) {

                    setError(
                        githubInput,
                        "Please enter a valid GitHub URL."
                    );

                    valid = false;

                }



                /* =========================================
                   PORTFOLIO
                   ========================================= */

                if (
                    valid &&
                    portfolioInput &&
                    !isValidUrl(
                        portfolioInput.value.trim()
                    )
                ) {

                    setError(
                        portfolioInput,
                        "Please enter a valid portfolio URL."
                    );

                    valid = false;

                }



                /* =========================================
                   INVALID FORM
                   ========================================= */

                if (!valid) {

                    event.preventDefault();

                    return;

                }



                /* =========================================
                   SAVE BUTTON
                   ========================================= */

                if (saveButton) {

                    saveButton.disabled = true;


                    const buttonText =
                        saveButton.querySelector(
                            "span"
                        );


                    if (buttonText) {

                        buttonText.textContent =
                            "Saving...";

                    }

                }

            }
        );

    }
);