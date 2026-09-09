document.addEventListener("DOMContentLoaded", function () {

    const form =
        document.getElementById("collegeProfileForm");

    const saveButton =
        document.getElementById("saveProfileBtn");


    /* =====================================================
       HELPERS
    ====================================================== */

    function setError(fieldId, errorId, message) {

        const field =
            document.getElementById(fieldId);

        const error =
            document.getElementById(errorId);

        if (!field || !error) {
            return;
        }

        const group =
            field.closest(".form-group");

        error.textContent = message;

        if (message) {
            group.classList.add("has-error");
            group.classList.remove("has-success");
        } else {
            group.classList.remove("has-error");
        }
    }


    function clearErrors() {

        document
            .querySelectorAll(".field-error")
            .forEach(function (element) {
                element.textContent = "";
            });

        document
            .querySelectorAll(".form-group")
            .forEach(function (group) {
                group.classList.remove("has-error");
                group.classList.remove("has-success");
            });
    }


    function markSuccess(fieldId) {

        const field =
            document.getElementById(fieldId);

        if (!field) {
            return;
        }

        const group =
            field.closest(".form-group");

        group.classList.remove("has-error");
        group.classList.add("has-success");
    }


    /* =====================================================
       PHONE INPUT
    ====================================================== */

    const phone =
        document.getElementById("phone");

    if (phone) {

        phone.addEventListener("input", function () {

            this.value =
                this.value
                    .replace(/\D/g, "")
                    .slice(0, 10);

        });

    }


    /* =====================================================
       PINCODE INPUT
    ====================================================== */

    const pincode =
        document.getElementById("pincode");

    if (pincode) {

        pincode.addEventListener("input", function () {

            this.value =
                this.value
                    .replace(/\D/g, "")
                    .slice(0, 6);

        });

    }


    /* =====================================================
       FORM VALIDATION
    ====================================================== */

    if (form) {

        form.addEventListener("submit", function (event) {

            clearErrors();

            let valid = true;


            const collegeName =
                document
                    .getElementById("college_name")
                    .value
                    .trim();

            const university =
                document
                    .getElementById("university_name")
                    .value
                    .trim();

            const contactPerson =
                document
                    .getElementById("contact_person")
                    .value
                    .trim();

            const phoneValue =
                document
                    .getElementById("phone")
                    .value
                    .trim();

            const address =
                document
                    .getElementById("address")
                    .value
                    .trim();

            const city =
                document
                    .getElementById("city")
                    .value
                    .trim();

            const state =
                document
                    .getElementById("state")
                    .value
                    .trim();

            const pincodeValue =
                document
                    .getElementById("pincode")
                    .value
                    .trim();

            const website =
                document
                    .getElementById("website")
                    .value
                    .trim();


            /* ------------------------------------------------
               COLLEGE NAME
            ------------------------------------------------ */

            if (!collegeName) {

                setError(
                    "college_name",
                    "collegeNameError",
                    "College name is required."
                );

                valid = false;

            } else {

                markSuccess("college_name");

            }


            /* ------------------------------------------------
               UNIVERSITY
            ------------------------------------------------ */

            if (!university) {

                setError(
                    "university_name",
                    "universityError",
                    "University name is required."
                );

                valid = false;

            } else {

                markSuccess("university_name");

            }


            /* ------------------------------------------------
               CONTACT PERSON
            ------------------------------------------------ */

            if (!contactPerson) {

                setError(
                    "contact_person",
                    "contactPersonError",
                    "Contact person is required."
                );

                valid = false;

            } else {

                markSuccess("contact_person");

            }


            /* ------------------------------------------------
               PHONE
            ------------------------------------------------ */

            if (!/^\d{10}$/.test(phoneValue)) {

                setError(
                    "phone",
                    "phoneError",
                    "Enter a valid 10-digit phone number."
                );

                valid = false;

            } else {

                markSuccess("phone");

            }


            /* ------------------------------------------------
               ADDRESS
            ------------------------------------------------ */

            if (!address) {

                setError(
                    "address",
                    "addressError",
                    "Address is required."
                );

                valid = false;

            } else {

                markSuccess("address");

            }


            /* ------------------------------------------------
               CITY
            ------------------------------------------------ */

            if (!city) {

                setError(
                    "city",
                    "cityError",
                    "City is required."
                );

                valid = false;

            } else {

                markSuccess("city");

            }


            /* ------------------------------------------------
               STATE
            ------------------------------------------------ */

            if (!state) {

                setError(
                    "state",
                    "stateError",
                    "State is required."
                );

                valid = false;

            } else {

                markSuccess("state");

            }


            /* ------------------------------------------------
               PINCODE
            ------------------------------------------------ */

            if (!/^\d{6}$/.test(pincodeValue)) {

                setError(
                    "pincode",
                    "pincodeError",
                    "Enter a valid 6-digit pincode."
                );

                valid = false;

            } else {

                markSuccess("pincode");

            }


            /* ------------------------------------------------
               WEBSITE
            ------------------------------------------------ */

            if (website) {

                const websitePattern =
                    /^https?:\/\/.+/i;

                if (!websitePattern.test(website)) {

                    setError(
                        "website",
                        "websiteError",
                        "Website must start with http:// or https://."
                    );

                    valid = false;

                } else {

                    markSuccess("website");

                }

            }


            /* ------------------------------------------------
               STOP INVALID SUBMISSION
            ------------------------------------------------ */

            if (!valid) {

                event.preventDefault();

                const firstError =
                    document.querySelector(
                        ".form-group.has-error input, " +
                        ".form-group.has-error textarea"
                    );

                if (firstError) {
                    firstError.focus();
                }

                return;
            }


            /* ------------------------------------------------
               SUBMIT STATE
            ------------------------------------------------ */

            if (saveButton) {

                saveButton.classList.add("loading");

                saveButton.disabled = true;

                saveButton.querySelector("span").textContent =
                    "Saving...";

                const icon =
                    saveButton.querySelector("i");

                if (icon) {
                    icon.className =
                        "fas fa-spinner fa-spin";
                }

            }

        });

    }


    /* =====================================================
       INPUT ANIMATION / CLEANUP
    ====================================================== */

    document
        .querySelectorAll(
            ".input-wrapper input:not([readonly]), " +
            ".textarea-wrapper textarea"
        )
        .forEach(function (field) {

            field.addEventListener("input", function () {

                const group =
                    this.closest(".form-group");

                if (group) {
                    group.classList.remove("has-error");
                }

            });

        });


    console.log(
        "SIH College Profile Edit loaded successfully."
    );

});