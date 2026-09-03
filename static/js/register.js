// =========================================================
// SIH PORTAL - REGISTRATION JAVASCRIPT
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    // No registration form on role-selection page
    if (!form) {
        return;
    }


    // =====================================================
    // INPUT ELEMENTS
    // =====================================================

    const nameInput =
        document.getElementById("name");

    const emailInput =
        document.getElementById("email");

    const passwordInput =
        document.getElementById("password");

    const confirmPasswordInput =
        document.getElementById("confirm_password");

    const passwordStrength =
        document.getElementById("password-strength");

    const passwordMatch =
        document.getElementById("password-match");


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

                // Length
                if (password.length >= 8) {
                    score++;
                }

                // Letters
                if (/[A-Za-z]/.test(password)) {
                    score++;
                }

                // Numbers
                if (/\d/.test(password)) {
                    score++;
                }

                // Special character
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
        else {

            passwordMatch.textContent =
                "Passwords do not match.";

            return false;
        }

    }


    if (confirmPasswordInput) {

        confirmPasswordInput.addEventListener(
            "input",
            checkPasswordMatch
        );

    }


    // =====================================================
    // FORM SUBMIT VALIDATION
    // =====================================================

    form.addEventListener(
        "submit",
        function (event) {

            // -------------------------------------------------
            // NAME
            // -------------------------------------------------

            const name =
                nameInput
                    ? nameInput.value.trim()
                    : "";


            if (name.length < 2) {

                event.preventDefault();

                alert(
                    "Please enter a valid name."
                );

                if (nameInput) {
                    nameInput.focus();
                }

                return;
            }


            // -------------------------------------------------
            // EMAIL
            // -------------------------------------------------

            const email =
                emailInput
                    ? emailInput.value.trim()
                    : "";


            const emailPattern =
                /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;


            if (!emailPattern.test(email)) {

                event.preventDefault();

                alert(
                    "Please enter a valid email address."
                );

                if (emailInput) {
                    emailInput.focus();
                }

                return;
            }


            // -------------------------------------------------
            // PASSWORD
            // -------------------------------------------------

            const password =
                passwordInput
                    ? passwordInput.value
                    : "";


            if (password.length < 6) {

                event.preventDefault();

                alert(
                    "Password must be at least 6 characters."
                );

                if (passwordInput) {
                    passwordInput.focus();
                }

                return;
            }


            // -------------------------------------------------
            // CONFIRM PASSWORD
            // -------------------------------------------------

            const passwordsMatch =
                checkPasswordMatch();


            if (!passwordsMatch) {

                event.preventDefault();

                alert(
                    "Passwords do not match."
                );

                if (confirmPasswordInput) {
                    confirmPasswordInput.focus();
                }

                return;
            }

        }
    );

});