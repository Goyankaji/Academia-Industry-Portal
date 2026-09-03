/* =========================================================
   SIH PORTAL
   PLACEMENT CELL REGISTRATION JAVASCRIPT
   ========================================================= */


document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =====================================================
           FORM
        ===================================================== */

        const form =
            document.getElementById(
                "placementRegisterForm"
            );


        if (!form) {
            return;
        }


        /* =====================================================
           INPUTS
        ===================================================== */

        const representativeNameInput =
            document.getElementById(
                "representative_name"
            );

        const emailInput =
            document.getElementById(
                "email"
            );

        const passwordInput =
            document.getElementById(
                "password"
            );

        const confirmPasswordInput =
            document.getElementById(
                "confirm_password"
            );

        const collegeInput =
            document.getElementById(
                "college_id"
            );

        const phoneInput =
            document.getElementById(
                "phone"
            );


        /* =====================================================
           ERROR ELEMENTS
        ===================================================== */

        const representativeNameError =
            document.getElementById(
                "representativeNameError"
            );

        const emailError =
            document.getElementById(
                "emailError"
            );

        const collegeError =
            document.getElementById(
                "collegeError"
            );

        const phoneError =
            document.getElementById(
                "phoneError"
            );


        /* =====================================================
           PASSWORD STATUS
        ===================================================== */

        const passwordStrength =
            document.getElementById(
                "passwordStrength"
            );

        const passwordMatch =
            document.getElementById(
                "passwordMatch"
            );


        /* =====================================================
           SUBMIT BUTTON
        ===================================================== */

        const submitButton =
            document.getElementById(
                "submitButton"
            );


        /* =====================================================
           NAME VALIDATION
        ===================================================== */

        function validateRepresentativeName() {

            const name =
                representativeNameInput.value.trim();

            representativeNameError.textContent = "";


            if (!name) {

                representativeNameError.textContent =
                    "Representative name is required.";

                return false;
            }


            if (name.length < 2) {

                representativeNameError.textContent =
                    "Please enter a valid name.";

                return false;
            }


            return true;
        }


        /* =====================================================
           EMAIL VALIDATION
        ===================================================== */

        function validateEmail() {

            const email =
                emailInput.value.trim();

            emailError.textContent = "";


            if (!email) {

                emailError.textContent =
                    "Email address is required.";

                return false;
            }


            const emailPattern =
                /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;


            if (!emailPattern.test(email)) {

                emailError.textContent =
                    "Please enter a valid email address.";

                return false;
            }


            return true;
        }


        /* =====================================================
           COLLEGE VALIDATION
        ===================================================== */

        function validateCollege() {

            collegeError.textContent = "";


            if (!collegeInput.value) {

                collegeError.textContent =
                    "Please select your college.";

                return false;
            }


            return true;
        }


        /* =====================================================
           PHONE VALIDATION
        ===================================================== */

        function validatePhone() {

            const phone =
                phoneInput.value.trim();

            phoneError.textContent = "";


            // Phone is optional

            if (!phone) {
                return true;
            }


            const phonePattern =
                /^[0-9]{10,15}$/;


            if (!phonePattern.test(phone)) {

                phoneError.textContent =
                    "Phone number must contain 10 to 15 digits.";

                return false;
            }


            return true;
        }


        /* =====================================================
           PASSWORD STRENGTH
        ===================================================== */

        passwordInput.addEventListener(
            "input",
            function () {

                const password =
                    passwordInput.value;


                if (!password) {

                    passwordStrength.textContent = "";

                    return;
                }


                if (password.length < 6) {

                    passwordStrength.textContent =
                        "Password must be at least 6 characters.";

                    return;
                }


                let score = 0;


                if (password.length >= 8) {
                    score++;
                }


                if (/[A-Za-z]/.test(password)) {
                    score++;
                }


                if (/\d/.test(password)) {
                    score++;
                }


                if (/[^A-Za-z0-9]/.test(password)) {
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


        /* =====================================================
           PASSWORD MATCH
        ===================================================== */

        function checkPasswordMatch() {

            const password =
                passwordInput.value;

            const confirmPassword =
                confirmPasswordInput.value;


            if (!confirmPassword) {

                passwordMatch.textContent = "";

                return false;
            }


            if (password === confirmPassword) {

                passwordMatch.textContent =
                    "Passwords match.";

                return true;

            }
            else {

                passwordMatch.textContent =
                    "Passwords do not match.";

                return false;

            }

        }


        confirmPasswordInput.addEventListener(
            "input",
            checkPasswordMatch
        );


        /* =====================================================
           REAL-TIME VALIDATION
        ===================================================== */

        representativeNameInput.addEventListener(
            "blur",
            validateRepresentativeName
        );


        emailInput.addEventListener(
            "blur",
            validateEmail
        );


        collegeInput.addEventListener(
            "change",
            validateCollege
        );


        phoneInput.addEventListener(
            "blur",
            validatePhone
        );


        /* =====================================================
           FORM SUBMIT
        ===================================================== */

        form.addEventListener(
            "submit",
            function (event) {


                const nameValid =
                    validateRepresentativeName();


                const emailValid =
                    validateEmail();


                const collegeValid =
                    validateCollege();


                const phoneValid =
                    validatePhone();


                const password =
                    passwordInput.value;


                const confirmPassword =
                    confirmPasswordInput.value;


                let passwordValid = true;


                if (!password) {

                    passwordValid = false;

                    alert(
                        "Password is required."
                    );

                    passwordInput.focus();

                    event.preventDefault();

                    return;
                }


                if (password.length < 6) {

                    passwordValid = false;

                    alert(
                        "Password must be at least 6 characters."
                    );

                    passwordInput.focus();

                    event.preventDefault();

                    return;
                }


                if (!confirmPassword) {

                    passwordValid = false;

                    alert(
                        "Please confirm your password."
                    );

                    confirmPasswordInput.focus();

                    event.preventDefault();

                    return;
                }


                const passwordsMatch =
                    checkPasswordMatch();


                if (
                    !nameValid ||
                    !emailValid ||
                    !collegeValid ||
                    !phoneValid ||
                    !passwordValid ||
                    !passwordsMatch
                ) {

                    event.preventDefault();

                    if (!nameValid) {

                        representativeNameInput.focus();

                    }
                    else if (!emailValid) {

                        emailInput.focus();

                    }
                    else if (!collegeValid) {

                        collegeInput.focus();

                    }
                    else if (!phoneValid) {

                        phoneInput.focus();

                    }
                    else if (!passwordsMatch) {

                        confirmPasswordInput.focus();

                    }

                    return;
                }


                /* =============================================
                   ALLOW FLASK SUBMISSION
                ============================================== */

                submitButton.disabled = true;

                submitButton.textContent =
                    "Creating Account...";

            }
        );

    }
);