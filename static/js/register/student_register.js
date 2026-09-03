/* =========================================================
   SIH PORTAL - STUDENT REGISTRATION JAVASCRIPT
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const form =
            document.getElementById(
                "studentRegisterForm"
            );


        if (!form) {
            return;
        }


        /* =================================================
           INPUTS
           ================================================= */

        const nameInput =
            document.getElementById("name");

        const emailInput =
            document.getElementById("email");

        const passwordInput =
            document.getElementById("password");

        const confirmPasswordInput =
            document.getElementById(
                "confirm_password"
            );

        const collegeInput =
            document.getElementById("college_id");

        const enrollmentInput =
            document.getElementById(
                "enrollment_no"
            );

        const courseInput =
            document.getElementById("course");

        const branchInput =
            document.getElementById("branch");


        /* =================================================
           ERROR ELEMENTS
           ================================================= */

        const nameError =
            document.getElementById("nameError");

        const emailError =
            document.getElementById("emailError");

        const passwordStrength =
            document.getElementById(
                "passwordStrength"
            );

        const passwordMatch =
            document.getElementById(
                "passwordMatch"
            );

        const collegeError =
            document.getElementById(
                "collegeError"
            );

        const enrollmentError =
            document.getElementById(
                "enrollmentError"
            );

        const courseError =
            document.getElementById(
                "courseError"
            );

        const branchError =
            document.getElementById(
                "branchError"
            );


        /* =================================================
           HELPER
           ================================================= */

        function setError(
            input,
            errorElement,
            message
        ) {

            if (input) {
                input.classList.add("invalid");
                input.classList.remove("valid");
            }

            if (errorElement) {
                errorElement.textContent = message;
            }

            return false;
        }


        function setValid(
            input,
            errorElement
        ) {

            if (input) {
                input.classList.remove("invalid");
                input.classList.add("valid");
            }

            if (errorElement) {
                errorElement.textContent = "";
            }

            return true;
        }


        /* =================================================
           NAME
           ================================================= */

        function validateName() {

            const value =
                nameInput.value.trim();

            if (!value) {

                return setError(
                    nameInput,
                    nameError,
                    "Full name is required."
                );
            }


            if (value.length < 2) {

                return setError(
                    nameInput,
                    nameError,
                    "Name must contain at least 2 characters."
                );
            }


            return setValid(
                nameInput,
                nameError
            );
        }


        /* =================================================
           EMAIL
           ================================================= */

        function validateEmail() {

            const value =
                emailInput.value.trim();

            const pattern =
                /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;


            if (!value) {

                return setError(
                    emailInput,
                    emailError,
                    "Email address is required."
                );
            }


            if (!pattern.test(value)) {

                return setError(
                    emailInput,
                    emailError,
                    "Please enter a valid email address."
                );
            }


            return setValid(
                emailInput,
                emailError
            );
        }


        /* =================================================
           PASSWORD
           ================================================= */

        function validatePassword() {

            const password =
                passwordInput.value;


            if (!password) {

                passwordStrength.textContent =
                    "Password is required.";

                return false;
            }


            if (password.length < 6) {

                passwordStrength.textContent =
                    "Password must be at least 6 characters.";

                return false;
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


            return true;
        }


        /* =================================================
           PASSWORD MATCH
           ================================================= */

        function validatePasswordMatch() {

            const password =
                passwordInput.value;

            const confirmPassword =
                confirmPasswordInput.value;


            if (!confirmPassword) {

                passwordMatch.textContent =
                    "Please confirm your password.";

                return false;
            }


            if (password !== confirmPassword) {

                passwordMatch.textContent =
                    "Passwords do not match.";

                return false;
            }


            passwordMatch.textContent =
                "Passwords match.";

            return true;
        }


        /* =================================================
           COLLEGE
           ================================================= */

        function validateCollege() {

            if (!collegeInput.value) {

                return setError(
                    collegeInput,
                    collegeError,
                    "Please select your college."
                );
            }


            return setValid(
                collegeInput,
                collegeError
            );
        }


        /* =================================================
           ENROLLMENT
           ================================================= */

        function validateEnrollment() {

            const value =
                enrollmentInput.value.trim();


            if (!value) {

                return setError(
                    enrollmentInput,
                    enrollmentError,
                    "Enrollment number is required."
                );
            }


            return setValid(
                enrollmentInput,
                enrollmentError
            );
        }


        /* =================================================
           COURSE
           ================================================= */

        function validateCourse() {

            const value =
                courseInput.value.trim();


            if (!value) {

                return setError(
                    courseInput,
                    courseError,
                    "Course is required."
                );
            }


            return setValid(
                courseInput,
                courseError
            );
        }


        /* =================================================
           BRANCH
           ================================================= */

        function validateBranch() {

            const value =
                branchInput.value.trim();


            if (!value) {

                return setError(
                    branchInput,
                    branchError,
                    "Branch is required."
                );
            }


            return setValid(
                branchInput,
                branchError
            );
        }


        /* =================================================
           REAL-TIME VALIDATION
           ================================================= */

        nameInput.addEventListener(
            "blur",
            validateName
        );


        emailInput.addEventListener(
            "blur",
            validateEmail
        );


        passwordInput.addEventListener(
            "input",
            function () {

                validatePassword();

                if (
                    confirmPasswordInput.value
                ) {
                    validatePasswordMatch();
                }

            }
        );


        confirmPasswordInput.addEventListener(
            "input",
            validatePasswordMatch
        );


        collegeInput.addEventListener(
            "change",
            validateCollege
        );


        enrollmentInput.addEventListener(
            "blur",
            validateEnrollment
        );


        courseInput.addEventListener(
            "blur",
            validateCourse
        );


        branchInput.addEventListener(
            "blur",
            validateBranch
        );


        /* =================================================
           FORM SUBMIT
           ================================================= */

        form.addEventListener(
            "submit",
            function (event) {

                const validName =
                    validateName();

                const validEmail =
                    validateEmail();

                const validPassword =
                    validatePassword();

                const validMatch =
                    validatePasswordMatch();

                const validCollege =
                    validateCollege();

                const validEnrollment =
                    validateEnrollment();

                const validCourse =
                    validateCourse();

                const validBranch =
                    validateBranch();


                const isValid =
                    validName &&
                    validEmail &&
                    validPassword &&
                    validMatch &&
                    validCollege &&
                    validEnrollment &&
                    validCourse &&
                    validBranch;


                if (!isValid) {

                    event.preventDefault();

                    const firstInvalid =
                        form.querySelector(
                            ".invalid"
                        );

                    if (firstInvalid) {
                        firstInvalid.focus();
                    }

                    return;
                }


                /*
                 * Validation passed.
                 *
                 * Do NOT prevent submission.
                 * Flask will receive the form data.
                 */

                const button =
                    document.getElementById(
                        "studentRegisterButton"
                    );


                if (button) {

                    button.disabled = true;

                    button.textContent =
                        "Creating Account...";
                }

            }
        );

    }
);