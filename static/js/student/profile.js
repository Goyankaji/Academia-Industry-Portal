/* =========================================================
   STUDENT PROFILE JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       PROFILE FORM
       ===================================================== */

    const profileForm = document.querySelector(
        ".profile-form"
    );


    if (!profileForm) {
        return;
    }


    /* =====================================================
       FORM INPUTS
       ===================================================== */

    const nameInput = document.getElementById("name");

    const phoneInput = document.getElementById("phone");

    const dobInput = document.getElementById("dob");

    const genderInput = document.getElementById("gender");

    const addressInput = document.getElementById("address");

    const linkedinInput =
        document.getElementById("linkedin_url");

    const githubInput =
        document.getElementById("github_url");

    const portfolioInput =
        document.getElementById("portfolio_url");

    const resumeInput =
        document.getElementById("resume_url");


    /* =====================================================
       NAME VALIDATION
       ===================================================== */

    if (nameInput) {

        nameInput.addEventListener(
            "input",
            function () {

                const value =
                    nameInput.value.trim();

                if (value.length === 0) {

                    nameInput.classList.add(
                        "input-error"
                    );

                    nameInput.classList.remove(
                        "input-valid"
                    );

                } else {

                    nameInput.classList.remove(
                        "input-error"
                    );

                    nameInput.classList.add(
                        "input-valid"
                    );
                }

            }
        );

    }


    /* =====================================================
       PHONE VALIDATION
       ===================================================== */

    if (phoneInput) {

        phoneInput.addEventListener(
            "input",
            function () {

                /*
                 * Allow digits, spaces, +, -, brackets.
                 */

                phoneInput.value =
                    phoneInput.value.replace(
                        /[^0-9+\-\s()]/g,
                        ""
                    );


                const value =
                    phoneInput.value.trim();


                /*
                 * Phone is optional.
                 * Validate only when entered.
                 */

                if (value.length === 0) {

                    phoneInput.classList.remove(
                        "input-error",
                        "input-valid"
                    );

                    return;
                }


                const digits =
                    value.replace(
                        /\D/g,
                        ""
                    );


                if (
                    digits.length >= 10 &&
                    digits.length <= 15
                ) {

                    phoneInput.classList.remove(
                        "input-error"
                    );

                    phoneInput.classList.add(
                        "input-valid"
                    );

                } else {

                    phoneInput.classList.add(
                        "input-error"
                    );

                    phoneInput.classList.remove(
                        "input-valid"
                    );

                }

            }
        );

    }


    /* =====================================================
       URL VALIDATION
       ===================================================== */

    function validateUrl(input) {

        if (!input) {
            return;
        }


        const value =
            input.value.trim();


        /*
         * URL fields are optional.
         */

        if (value.length === 0) {

            input.classList.remove(
                "input-error",
                "input-valid"
            );

            return;
        }


        try {

            const url =
                new URL(value);


            if (
                url.protocol === "http:" ||
                url.protocol === "https:"
            ) {

                input.classList.remove(
                    "input-error"
                );

                input.classList.add(
                    "input-valid"
                );

            } else {

                input.classList.add(
                    "input-error"
                );

                input.classList.remove(
                    "input-valid"
                );

            }

        } catch (error) {

            input.classList.add(
                "input-error"
            );

            input.classList.remove(
                "input-valid"
            );

        }

    }


    if (linkedinInput) {

        linkedinInput.addEventListener(
            "input",
            function () {
                validateUrl(linkedinInput);
            }
        );

    }


    if (githubInput) {

        githubInput.addEventListener(
            "input",
            function () {
                validateUrl(githubInput);
            }
        );

    }


    if (portfolioInput) {

        portfolioInput.addEventListener(
            "input",
            function () {
                validateUrl(portfolioInput);
            }
        );

    }


    if (resumeInput) {

        resumeInput.addEventListener(
            "input",
            function () {
                validateUrl(resumeInput);
            }
        );

    }


    /* =====================================================
       ADDRESS CHARACTER HANDLING
       ===================================================== */

    if (addressInput) {

        addressInput.addEventListener(
            "input",
            function () {

                /*
                 * Remove unnecessary leading spaces.
                 */

                addressInput.value =
                    addressInput.value.replace(
                        /^\s+/,
                        ""
                    );

            }
        );

    }


    /* =====================================================
       DATE OF BIRTH
       ===================================================== */

    if (dobInput) {

        /*
         * Do not allow a future date of birth.
         */

        const today =
            new Date()
                .toISOString()
                .split("T")[0];

        dobInput.setAttribute(
            "max",
            today
        );

    }


    /* =====================================================
       FORM SUBMIT VALIDATION
       ===================================================== */

    profileForm.addEventListener(
        "submit",
        function (event) {

            let isValid = true;


            /* ---------------------------------------------
               NAME
            --------------------------------------------- */

            if (nameInput) {

                const name =
                    nameInput.value.trim();


                if (name.length === 0) {

                    event.preventDefault();

                    nameInput.classList.add(
                        "input-error"
                    );

                    nameInput.focus();

                    isValid = false;

                }

            }


            /* ---------------------------------------------
               PHONE
            --------------------------------------------- */

            if (
                isValid &&
                phoneInput
            ) {

                const phone =
                    phoneInput.value.trim();


                if (phone.length > 0) {

                    const digits =
                        phone.replace(
                            /\D/g,
                            ""
                        );


                    if (
                        digits.length < 10 ||
                        digits.length > 15
                    ) {

                        event.preventDefault();

                        phoneInput.classList.add(
                            "input-error"
                        );

                        phoneInput.focus();

                        isValid = false;

                    }

                }

            }


            /* ---------------------------------------------
               DATE OF BIRTH
            --------------------------------------------- */

            if (
                isValid &&
                dobInput &&
                dobInput.value
            ) {

                const selectedDate =
                    new Date(
                        dobInput.value
                    );

                const today =
                    new Date();


                today.setHours(
                    0,
                    0,
                    0,
                    0
                );


                if (selectedDate > today) {

                    event.preventDefault();

                    dobInput.classList.add(
                        "input-error"
                    );

                    dobInput.focus();

                    isValid = false;

                }

            }


            /* ---------------------------------------------
               URL FIELDS
            --------------------------------------------- */

            if (isValid) {

                const urlInputs = [
                    linkedinInput,
                    githubInput,
                    portfolioInput,
                    resumeInput
                ];


                for (
                    let i = 0;
                    i < urlInputs.length;
                    i++
                ) {

                    const input =
                        urlInputs[i];


                    if (!input) {
                        continue;
                    }


                    const value =
                        input.value.trim();


                    if (value.length === 0) {
                        continue;
                    }


                    try {

                        const url =
                            new URL(value);


                        if (
                            url.protocol !== "http:" &&
                            url.protocol !== "https:"
                        ) {

                            throw new Error(
                                "Invalid protocol"
                            );

                        }

                    } catch (error) {

                        event.preventDefault();

                        input.classList.add(
                            "input-error"
                        );

                        input.focus();

                        isValid = false;

                        break;
                    }

                }

            }


            /* ---------------------------------------------
               FINAL CHECK
            --------------------------------------------- */

            if (!isValid) {

                event.preventDefault();

                return;
            }


            /*
             * Prevent accidental double submission.
             */

            const submitButton =
                profileForm.querySelector(
                    'button[type="submit"]'
                );


            if (submitButton) {

                submitButton.disabled = true;

                submitButton.textContent =
                    "Saving...";

            }

        }
    );


    /* =====================================================
       RESET BUTTON
       ===================================================== */

    const resetButton =
        profileForm.querySelector(
            'button[type="reset"]'
        );


    if (resetButton) {

        resetButton.addEventListener(
            "click",
            function () {

                /*
                 * Remove validation styling.
                 */

                const fields =
                    profileForm.querySelectorAll(
                        "input, select, textarea"
                    );


                fields.forEach(
                    function (field) {

                        field.classList.remove(
                            "input-error",
                            "input-valid"
                        );

                    }
                );

            }
        );

    }


    /* =====================================================
       INITIAL URL VALIDATION
       ===================================================== */

    validateUrl(linkedinInput);

    validateUrl(githubInput);

    validateUrl(portfolioInput);

    validateUrl(resumeInput);


    /* =====================================================
       PROFILE READY
       ===================================================== */

    document.body.classList.add(
        "student-profile-ready"
    );

});