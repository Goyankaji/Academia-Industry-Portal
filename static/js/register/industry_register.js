/* =========================================================
   SIH PORTAL - INDUSTRY REGISTRATION JAVASCRIPT
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const form =
            document.getElementById(
                "industryRegisterForm"
            );

        if (!form) {
            return;
        }


        /* =================================================
           INPUTS
        ================================================= */

        const contactPerson =
            document.getElementById(
                "contact_person"
            );

        const email =
            document.getElementById(
                "email"
            );

        const password =
            document.getElementById(
                "password"
            );

        const confirmPassword =
            document.getElementById(
                "confirm_password"
            );

        const companyName =
            document.getElementById(
                "company_name"
            );

        const website =
            document.getElementById(
                "website"
            );

        const phone =
            document.getElementById(
                "phone"
            );


        /* =================================================
           ERROR ELEMENTS
        ================================================= */

        const contactPersonError =
            document.getElementById(
                "contactPersonError"
            );

        const emailError =
            document.getElementById(
                "emailError"
            );

        const companyNameError =
            document.getElementById(
                "companyNameError"
            );

        const passwordStrength =
            document.getElementById(
                "passwordStrength"
            );

        const passwordMatch =
            document.getElementById(
                "passwordMatch"
            );


        /* =================================================
           PASSWORD STRENGTH
        ================================================= */

        password.addEventListener(
            "input",
            function () {

                const value =
                    password.value;

                if (!value) {

                    passwordStrength.textContent =
                        "";

                    return;
                }


                if (value.length < 6) {

                    passwordStrength.textContent =
                        "Password must be at least 6 characters.";

                    return;
                }


                let score = 0;


                if (value.length >= 8) {
                    score++;
                }


                if (/[A-Za-z]/.test(value)) {
                    score++;
                }


                if (/\d/.test(value)) {
                    score++;
                }


                if (/[^A-Za-z0-9]/.test(value)) {
                    score++;
                }


                if (score <= 1) {

                    passwordStrength.textContent =
                        "Password strength: Weak";

                }
                else if (score <= 3) {

                    passwordStrength.textContent =
                        "Password strength: Good";

                }
                else {

                    passwordStrength.textContent =
                        "Password strength: Strong";

                }

            }
        );


        /* =================================================
           PASSWORD MATCH
        ================================================= */

        function checkPasswordMatch() {

            if (
                !confirmPassword.value
            ) {

                passwordMatch.textContent =
                    "";

                return true;
            }


            if (
                password.value ===
                confirmPassword.value
            ) {

                passwordMatch.textContent =
                    "Passwords match.";

                return true;

            }


            passwordMatch.textContent =
                "Passwords do not match.";

            return false;
        }


        confirmPassword.addEventListener(
            "input",
            checkPasswordMatch
        );


        /* =================================================
           EMAIL VALIDATION
        ================================================= */

        function validateEmail() {

            const value =
                email.value.trim();


            if (!value) {

                emailError.textContent =
                    "Email address is required.";

                return false;
            }


            const pattern =
                /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;


            if (!pattern.test(value)) {

                emailError.textContent =
                    "Please enter a valid email address.";

                return false;
            }


            emailError.textContent =
                "";

            return true;
        }


        email.addEventListener(
            "blur",
            validateEmail
        );


        email.addEventListener(
            "input",
            function () {

                if (emailError.textContent) {
                    validateEmail();
                }

            }
        );


        /* =================================================
           FORM SUBMIT
        ================================================= */

        form.addEventListener(
            "submit",
            function (event) {

                let valid = true;


                /* -----------------------------------------
                   CONTACT PERSON
                ------------------------------------------ */

                if (
                    contactPerson.value.trim().length < 2
                ) {

                    contactPersonError.textContent =
                        "Please enter a valid contact person name.";

                    valid = false;

                }
                else {

                    contactPersonError.textContent =
                        "";

                }


                /* -----------------------------------------
                   EMAIL
                ------------------------------------------ */

                if (!validateEmail()) {
                    valid = false;
                }


                /* -----------------------------------------
                   PASSWORD
                ------------------------------------------ */

                if (
                    password.value.length < 6
                ) {

                    passwordStrength.textContent =
                        "Password must be at least 6 characters.";

                    valid = false;

                }


                /* -----------------------------------------
                   CONFIRM PASSWORD
                ------------------------------------------ */

                if (!checkPasswordMatch()) {
                    valid = false;
                }


                /* -----------------------------------------
                   COMPANY NAME
                ------------------------------------------ */

                if (
                    companyName.value.trim().length < 2
                ) {

                    companyNameError.textContent =
                        "Company name is required.";

                    valid = false;

                }
                else {

                    companyNameError.textContent =
                        "";

                }


                /* -----------------------------------------
                   PHONE
                ------------------------------------------ */

                if (phone.value.trim()) {

                    const phonePattern =
                        /^[0-9+\-\s]{7,15}$/;

                    if (
                        !phonePattern.test(
                            phone.value.trim()
                        )
                    ) {

                        alert(
                            "Please enter a valid phone number."
                        );

                        valid = false;
                    }

                }


                /* -----------------------------------------
                   WEBSITE
                ------------------------------------------ */

                if (website.value.trim()) {

                    try {

                        new URL(
                            website.value.trim()
                        );

                    }
                    catch (error) {

                        alert(
                            "Please enter a valid website URL."
                        );

                        valid = false;
                    }

                }


                /* -----------------------------------------
                   STOP SUBMISSION
                ------------------------------------------ */

                if (!valid) {

                    event.preventDefault();

                    return;
                }


                /* -----------------------------------------
                   SUBMITTING
                ------------------------------------------ */

                const button =
                    document.getElementById(
                        "industryRegisterButton"
                    );

                if (button) {

                    button.disabled = true;

                    button.textContent =
                        "Creating Industry Account...";

                }

            }
        );

    }
);