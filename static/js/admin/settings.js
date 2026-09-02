document.addEventListener("DOMContentLoaded", function () {

    console.log("SIH Admin Settings JS loaded successfully.");


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const saveProfile =
        document.getElementById("saveProfile");

    const changePassword =
        document.getElementById("changePassword");

    const saveNotifications =
        document.getElementById("saveNotifications");

    const saveAppearance =
        document.getElementById("saveAppearance");


    /* =====================================================
       SHOW MESSAGE
       ===================================================== */

    function showMessage(elementId, message, success = true) {

        const element =
            document.getElementById(elementId);

        if (!element) {
            return;
        }

        element.textContent = message;

        element.style.color =
            success ? "#16a34a" : "#dc2626";


        setTimeout(function () {

            element.textContent = "";

        }, 2500);

    }


    /* =====================================================
       PROFILE
       ===================================================== */

    if (saveProfile) {

        saveProfile.addEventListener(
            "click",
            function () {

                const name =
                    document.getElementById("adminName").value.trim();

                const email =
                    document.getElementById("adminEmail").value.trim();


                if (!name) {

                    showMessage(
                        "profileMessage",
                        "Name is required.",
                        false
                    );

                    return;

                }


                if (!email) {

                    showMessage(
                        "profileMessage",
                        "Email is required.",
                        false
                    );

                    return;

                }


                /*
                 * Backend API will be connected here.
                 * For now this validates the form.
                 */

                showMessage(
                    "profileMessage",
                    "Profile details ready to save."
                );

            }
        );

    }


    /* =====================================================
       CHANGE PASSWORD
       ===================================================== */

    if (changePassword) {

        changePassword.addEventListener(
            "click",
            function () {

                const currentPassword =
                    document.getElementById(
                        "currentPassword"
                    ).value;

                const newPassword =
                    document.getElementById(
                        "newPassword"
                    ).value;

                const confirmPassword =
                    document.getElementById(
                        "confirmPassword"
                    ).value;


                if (!currentPassword) {

                    showMessage(
                        "passwordMessage",
                        "Enter your current password.",
                        false
                    );

                    return;

                }


                if (!newPassword) {

                    showMessage(
                        "passwordMessage",
                        "Enter a new password.",
                        false
                    );

                    return;

                }


                if (newPassword.length < 6) {

                    showMessage(
                        "passwordMessage",
                        "Password must be at least 6 characters.",
                        false
                    );

                    return;

                }


                if (newPassword !== confirmPassword) {

                    showMessage(
                        "passwordMessage",
                        "Passwords do not match.",
                        false
                    );

                    return;

                }


                /*
                 * Backend password update will be
                 * connected here.
                 */

                showMessage(
                    "passwordMessage",
                    "Password details validated."
                );

            }
        );

    }


    /* =====================================================
       NOTIFICATION PREFERENCES
       ===================================================== */

    if (saveNotifications) {

        saveNotifications.addEventListener(
            "click",
            function () {

                const registrations =
                    document.getElementById(
                        "registrationNotifications"
                    ).checked;

                const collaborations =
                    document.getElementById(
                        "collaborationNotifications"
                    ).checked;

                const opportunities =
                    document.getElementById(
                        "opportunityNotifications"
                    ).checked;


                console.log(
                    "Notification Preferences:",
                    {
                        registrations: registrations,
                        collaborations: collaborations,
                        opportunities: opportunities
                    }
                );


                showMessage(
                    "notificationMessage",
                    "Notification preferences saved."
                );

            }
        );

    }


    /* =====================================================
       THEME SELECTION
       ===================================================== */

    const themeOptions =
        document.querySelectorAll(
            ".theme-option"
        );

    const themeInputs =
        document.querySelectorAll(
            'input[name="theme"]'
        );


    themeInputs.forEach(function (input) {

        input.addEventListener(
            "change",
            function () {

                themeOptions.forEach(
                    function (option) {

                        option.classList.remove(
                            "active"
                        );

                    }
                );


                const parent =
                    input.closest(".theme-option");


                if (parent) {

                    parent.classList.add(
                        "active"
                    );

                }

            }
        );

    });


    /* =====================================================
       SAVE APPEARANCE
       ===================================================== */

    if (saveAppearance) {

        saveAppearance.addEventListener(
            "click",
            function () {

                const selectedTheme =
                    document.querySelector(
                        'input[name="theme"]:checked'
                    );


                if (!selectedTheme) {
                    return;
                }


                console.log(
                    "Selected Theme:",
                    selectedTheme.value
                );


                showMessage(
                    "appearanceMessage",
                    "Appearance preference saved."
                );

            }
        );

    }

});