/* =========================================================
   SIH PORTAL - LOGIN JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const loginForm = document.getElementById("loginForm");

    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    const emailError = document.getElementById("emailError");
    const passwordError = document.getElementById("passwordError");

    const passwordToggle = document.getElementById("passwordToggle");
    const eyeIcon = document.getElementById("eyeIcon");

    const loginButton = document.getElementById("loginButton");

    const forgotPassword = document.getElementById("forgotPassword");


    /* =====================================================
       PASSWORD SHOW / HIDE
       ===================================================== */

    passwordToggle.addEventListener("click", function () {

        const isPassword =
            passwordInput.type === "password";

        if (isPassword) {

            passwordInput.type = "text";

            passwordToggle.setAttribute(
                "aria-label",
                "Hide password"
            );

            eyeIcon.innerHTML = `
                <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/>
                <path d="M4 4l16 16"/>
            `;

        } else {

            passwordInput.type = "password";

            passwordToggle.setAttribute(
                "aria-label",
                "Show password"
            );

            eyeIcon.innerHTML = `
                <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/>
                <circle cx="12" cy="12" r="3"/>
            `;
        }

    });


    /* =====================================================
       EMAIL VALIDATION
       ===================================================== */

    function validateEmail() {

        const email = emailInput.value.trim();

        emailError.textContent = "";

        if (!email) {

            emailError.textContent =
                "Email address is required.";

            return false;
        }

        const emailPattern =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email)) {

            emailError.textContent =
                "Please enter a valid email address.";

            return false;
        }

        return true;
    }


    /* =====================================================
       PASSWORD VALIDATION
       ===================================================== */

    function validatePassword() {

        const password = passwordInput.value;

        passwordError.textContent = "";

        if (!password) {

            passwordError.textContent =
                "Password is required.";

            return false;
        }

        return true;
    }


    /* =====================================================
       REAL-TIME FIELD VALIDATION
       ===================================================== */

    emailInput.addEventListener("blur", function () {
        validateEmail();
    });


    passwordInput.addEventListener("blur", function () {
        validatePassword();
    });


    emailInput.addEventListener("input", function () {

        if (emailError.textContent) {
            validateEmail();
        }

    });


    passwordInput.addEventListener("input", function () {

        if (passwordError.textContent) {
            validatePassword();
        }

    });


    /* =====================================================
       LOGIN FORM SUBMIT
       ===================================================== */

    loginForm.addEventListener("submit", function (event) {

        const emailValid = validateEmail();
        const passwordValid = validatePassword();

        if (!emailValid || !passwordValid) {

            event.preventDefault();

            return;
        }


        /*
         * Do NOT prevent submission here.
         *
         * Flask will receive:
         * email
         * password
         *
         * and perform authentication.
         */

        loginButton.disabled = true;

        loginButton.classList.add("loading");

    });


    /* =====================================================
       FORGOT PASSWORD
       ===================================================== */

    forgotPassword.addEventListener("click", function (event) {

        event.preventDefault();

        alert(
            "Password recovery will be available soon. " +
            "Please contact the portal administrator."
        );

    });

});