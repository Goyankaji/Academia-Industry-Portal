/* =========================================================
   INDUSTRY PROFILE
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       FORM
    ====================================================== */

    const profileForm =
        document.querySelector(".industry-profile-form");


    if (profileForm) {


        /* =================================================
           INPUT CLEANUP
        ================================================== */

        const textInputs =
            profileForm.querySelectorAll(
                'input[type="text"], textarea'
            );


        textInputs.forEach(function (input) {

            input.addEventListener(
                "blur",
                function () {

                    input.value =
                        input.value.trim();

                }
            );

        });


        /* =================================================
           PHONE VALIDATION
        ================================================== */

        const phoneInput =
            document.getElementById("phone");


        if (phoneInput) {

            phoneInput.addEventListener(
                "input",
                function () {

                    this.value =
                        this.value.replace(
                            /[^0-9+\-\s()]/g,
                            ""
                        );

                }
            );

        }


        /* =================================================
           FORM SUBMIT
        ================================================== */

        profileForm.addEventListener(
            "submit",
            function (event) {

                const requiredFields =
                    profileForm.querySelectorAll(
                        "[required]"
                    );

                let valid = true;


                requiredFields.forEach(
                    function (field) {

                        if (
                            !field.value ||
                            !field.value.trim()
                        ) {

                            valid = false;

                            field.classList.add(
                                "industry-profile-input-error"
                            );

                        } else {

                            field.classList.remove(
                                "industry-profile-input-error"
                            );

                        }

                    }
                );


                /* =========================================
                   EMAIL VALIDATION
                ========================================== */

                const emailInput =
                    document.getElementById("email");


                if (
                    emailInput &&
                    emailInput.value.trim()
                ) {

                    const emailPattern =
                        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


                    if (
                        !emailPattern.test(
                            emailInput.value.trim()
                        )
                    ) {

                        valid = false;

                        emailInput.classList.add(
                            "industry-profile-input-error"
                        );

                    }

                }


                /* =========================================
                   WEBSITE VALIDATION
                ========================================== */

                const websiteInput =
                    document.getElementById("website");


                if (
                    websiteInput &&
                    websiteInput.value.trim()
                ) {

                    try {

                        new URL(
                            websiteInput.value.trim()
                        );

                        websiteInput.classList.remove(
                            "industry-profile-input-error"
                        );

                    } catch (error) {

                        valid = false;

                        websiteInput.classList.add(
                            "industry-profile-input-error"
                        );

                    }

                }


                /* =========================================
                   STOP INVALID FORM
                ========================================== */

                if (!valid) {

                    event.preventDefault();

                    const firstError =
                        profileForm.querySelector(
                            ".industry-profile-input-error"
                        );


                    if (firstError) {

                        firstError.focus();

                    }

                    return;

                }


                /* =========================================
                   SUBMIT BUTTON
                ========================================== */

                const submitButton =
                    profileForm.querySelector(
                        'button[type="submit"]'
                    );


                if (submitButton) {

                    submitButton.disabled =
                        true;

                    submitButton.innerHTML =
                        "<span>✓</span> Saving...";

                }

            }
        );

    }


    /* =====================================================
       REMOVE INPUT ERROR ON CHANGE
    ====================================================== */

    const formInputs =
        document.querySelectorAll(
            ".industry-profile-form input, " +
            ".industry-profile-form textarea, " +
            ".industry-profile-form select"
        );


    formInputs.forEach(function (input) {

        input.addEventListener(
            "input",
            function () {

                this.classList.remove(
                    "industry-profile-input-error"
                );

            }
        );

    });


    /* =====================================================
       WEBSITE NORMALIZATION
    ====================================================== */

    const website =
        document.getElementById("website");


    if (website) {

        website.addEventListener(
            "blur",
            function () {

                let value =
                    this.value.trim();


                if (
                    value &&
                    !value.startsWith("http://") &&
                    !value.startsWith("https://")
                ) {

                    this.value =
                        "https://" + value;

                }

            }
        );

    }


});