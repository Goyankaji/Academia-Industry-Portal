// =========================================================
// SIH PORTAL - COLLEGE REGISTRATION JAVASCRIPT
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const form =
        document.getElementById("collegeRegisterForm");

    if (!form) {
        return;
    }


    // =====================================================
    // INPUTS
    // =====================================================

    const nameInput =
        document.getElementById("name");

    const emailInput =
        document.getElementById("email");

    const passwordInput =
        document.getElementById("password");

    const confirmPasswordInput =
        document.getElementById("confirm_password");

    const collegeNameInput =
        document.getElementById("college_name");

    const collegeCodeInput =
        document.getElementById("college_code");

    const collegeEmailInput =
        document.getElementById("college_email");

    const phoneInput =
        document.getElementById("phone");

    const pincodeInput =
        document.getElementById("pincode");

    const websiteInput =
        document.getElementById("website");


    // =====================================================
    // ERROR ELEMENTS
    // =====================================================

    const nameError =
        document.getElementById("nameError");

    const emailError =
        document.getElementById("emailError");

    const passwordStrength =
        document.getElementById("passwordStrength");

    const passwordMatch =
        document.getElementById("passwordMatch");

    const submitButton =
        document.getElementById("collegeRegisterButton");


    // =====================================================
    // EMAIL VALIDATION
    // =====================================================

    function isValidEmail(email) {

        const pattern =
            /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

        return pattern.test(email);
    }


    // =====================================================
    // PASSWORD STRENGTH
    // =====================================================

    if (passwordInput) {

        passwordInput.addEventListener(
            "input",
            function () {

                const password =
                    passwordInput.value;


                if (!passwordStrength) {
                    return;
                }


                if (password.length === 0) {

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

                } else if (score <= 3) {

                    passwordStrength.textContent =
                        "Password strength: Good";

                } else {

                    passwordStrength.textContent =
                        "Password strength: Strong";
                }

            }
        );

    }


    // =====================================================
    // PASSWORD MATCH
    // =====================================================

    function checkPasswordMatch() {

        if (
            !passwordInput ||
            !confirmPasswordInput ||
            !passwordMatch
        ) {

            return true;
        }


        const password =
            passwordInput.value;

        const confirmPassword =
            confirmPasswordInput.value;


        if (confirmPassword.length === 0) {

            passwordMatch.textContent = "";

            return true;
        }


        if (password === confirmPassword) {

            passwordMatch.textContent =
                "Passwords match.";

            return true;

        }


        passwordMatch.textContent =
            "Passwords do not match.";

        return false;
    }


    if (confirmPasswordInput) {

        confirmPasswordInput.addEventListener(
            "input",
            checkPasswordMatch
        );

    }


    // =====================================================
    // PHONE VALIDATION
    // =====================================================

    if (phoneInput) {

        phoneInput.addEventListener(
            "input",
            function () {

                phoneInput.value =
                    phoneInput.value.replace(
                        /[^0-9+ -]/g,
                        ""
                    );

            }
        );

    }


    // =====================================================
    // PINCODE VALIDATION
    // =====================================================

    if (pincodeInput) {

        pincodeInput.addEventListener(
            "input",
            function () {

                pincodeInput.value =
                    pincodeInput.value.replace(
                        /\D/g,
                        ""
                    );

            }
        );

    }


    // =====================================================
    // COLLEGE CODE
    // =====================================================

    if (collegeCodeInput) {

        collegeCodeInput.addEventListener(
            "input",
            function () {

                collegeCodeInput.value =
                    collegeCodeInput.value
                        .trim()
                        .toUpperCase();

            }
        );

    }


    // =====================================================
    // FORM SUBMIT
    // =====================================================

    form.addEventListener(
        "submit",
        function (event) {

            let valid = true;


            // -------------------------------------------------
            // CONTACT PERSON NAME
            // -------------------------------------------------

            const name =
                nameInput.value.trim();


            nameError.textContent = "";


            if (name.length < 2) {

                nameError.textContent =
                    "Please enter a valid name.";

                valid = false;
            }


            // -------------------------------------------------
            // LOGIN EMAIL
            // -------------------------------------------------

            const email =
                emailInput.value.trim();


            emailError.textContent = "";


            if (!isValidEmail(email)) {

                emailError.textContent =
                    "Please enter a valid email address.";

                valid = false;
            }


            // -------------------------------------------------
            // PASSWORD
            // -------------------------------------------------

            const password =
                passwordInput.value;


            if (password.length < 6) {

                alert(
                    "Password must be at least 6 characters."
                );

                valid = false;
            }


            // -------------------------------------------------
            // PASSWORD MATCH
            // -------------------------------------------------

            if (!checkPasswordMatch()) {

                alert(
                    "Passwords do not match."
                );

                valid = false;
            }


            // -------------------------------------------------
            // COLLEGE NAME
            // -------------------------------------------------

            if (
                !collegeNameInput.value.trim()
            ) {

                alert(
                    "College name is required."
                );

                valid = false;
            }


            // -------------------------------------------------
            // COLLEGE CODE
            // -------------------------------------------------

            if (
                !collegeCodeInput.value.trim()
            ) {

                alert(
                    "College code is required."
                );

                valid = false;
            }


            // -------------------------------------------------
            // COLLEGE EMAIL
            // -------------------------------------------------

            const collegeEmail =
                collegeEmailInput.value.trim();


            if (
                collegeEmail &&
                !isValidEmail(collegeEmail)
            ) {

                alert(
                    "Please enter a valid college email."
                );

                valid = false;
            }


            // -------------------------------------------------
            // PHONE
            // -------------------------------------------------

            const phone =
                phoneInput.value.trim();


            if (phone && phone.length < 10) {

                alert(
                    "Please enter a valid phone number."
                );

                valid = false;
            }


            // -------------------------------------------------
            // PINCODE
            // -------------------------------------------------

            const pincode =
                pincodeInput.value.trim();


            if (
                pincode &&
                (pincode.length < 4 ||
                 pincode.length > 10)
            ) {

                alert(
                    "Please enter a valid pincode."
                );

                valid = false;
            }


            // -------------------------------------------------
            // WEBSITE
            // -------------------------------------------------

            const website =
                websiteInput.value.trim();


            if (website) {

                try {

                    new URL(website);

                } catch (error) {

                    alert(
                        "Please enter a valid website URL."
                    );

                    valid = false;
                }

            }


            // =================================================
            // STOP SUBMISSION
            // =================================================

            if (!valid) {

                event.preventDefault();

                return;
            }


            // =================================================
            // SUBMITTING
            // =================================================

            submitButton.disabled = true;

            submitButton.textContent =
                "Creating Account...";

        }
    );

});