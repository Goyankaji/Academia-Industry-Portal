document.addEventListener("DOMContentLoaded", function () {

    console.log("SIH Admin Settings JS loaded successfully.");


    /* =====================================================
       COMMON MESSAGE FUNCTION
       ===================================================== */

    function showMessage(elementId, message, success = true) {

        const element = document.getElementById(elementId);

        if (!element) {
            return;
        }

        element.textContent = message;

        element.style.color = success
            ? "#16a34a"
            : "#dc2626";

        setTimeout(function () {
            element.textContent = "";
        }, 3000);
    }


    /* =====================================================
       HELPER - SEND FORM DATA
       ===================================================== */

    async function sendRequest(url, data) {

        const response = await fetch(url, {
            method: "POST",

            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },

            body: new URLSearchParams(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.message || "Something went wrong."
            );
        }

        return result;
    }


    /* =====================================================
       1. ADMIN PROFILE
       ===================================================== */

    const saveProfile =
        document.getElementById("saveProfile");

    if (saveProfile) {

        saveProfile.addEventListener("click", async function () {

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


            saveProfile.disabled = true;
            saveProfile.textContent = "Saving...";


            try {

                const result = await sendRequest(
                    "/admin/settings/profile",
                    {
                        name: name,
                        email: email
                    }
                );


                if (result.success) {

                    showMessage(
                        "profileMessage",
                        result.message,
                        true
                    );

                }

            } catch (error) {

                showMessage(
                    "profileMessage",
                    error.message,
                    false
                );

            } finally {

                saveProfile.disabled = false;
                saveProfile.textContent = "Save Changes";

            }

        });

    }


    /* =====================================================
       2. CHANGE PASSWORD
       ===================================================== */

    const changePassword =
        document.getElementById("changePassword");

    if (changePassword) {

        changePassword.addEventListener("click", async function () {

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
                    "New passwords do not match.",
                    false
                );

                return;
            }


            changePassword.disabled = true;
            changePassword.textContent = "Updating...";


            try {

                const result = await sendRequest(
                    "/admin/settings/password",
                    {
                        current_password: currentPassword,
                        new_password: newPassword,
                        confirm_password: confirmPassword
                    }
                );


                if (result.success) {

                    showMessage(
                        "passwordMessage",
                        result.message,
                        true
                    );


                    /*
                     * Clear password fields after
                     * successful update.
                     */

                    document.getElementById(
                        "currentPassword"
                    ).value = "";

                    document.getElementById(
                        "newPassword"
                    ).value = "";

                    document.getElementById(
                        "confirmPassword"
                    ).value = "";

                }

            } catch (error) {

                showMessage(
                    "passwordMessage",
                    error.message,
                    false
                );

            } finally {

                changePassword.disabled = false;
                changePassword.textContent = "Update Password";

            }

        });

    }


    /* =====================================================
       3. NOTIFICATION PREFERENCES
       ===================================================== */

    const saveNotifications =
        document.getElementById("saveNotifications");


    if (saveNotifications) {

        saveNotifications.addEventListener(
            "click",
            async function () {

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


                saveNotifications.disabled = true;
                saveNotifications.textContent = "Saving...";


                try {

                    const result = await sendRequest(
                        "/admin/settings/notifications",
                        {
                            notify_registrations:
                                registrations ? "true" : "false",

                            notify_collaborations:
                                collaborations ? "true" : "false",

                            notify_opportunities:
                                opportunities ? "true" : "false"
                        }
                    );


                    if (result.success) {

                        showMessage(
                            "notificationMessage",
                            result.message,
                            true
                        );

                    }

                } catch (error) {

                    showMessage(
                        "notificationMessage",
                        error.message,
                        false
                    );

                } finally {

                    saveNotifications.disabled = false;
                    saveNotifications.textContent =
                        "Save Preferences";

                }

            }
        );

    }


    /* =====================================================
       4. THEME SELECTION
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
       5. SAVE APPEARANCE
       ===================================================== */

    const saveAppearance =
        document.getElementById("saveAppearance");


    if (saveAppearance) {

        saveAppearance.addEventListener(
            "click",
            async function () {

                const selectedTheme =
                    document.querySelector(
                        'input[name="theme"]:checked'
                    );


                if (!selectedTheme) {

                    showMessage(
                        "appearanceMessage",
                        "Please select a theme.",
                        false
                    );

                    return;
                }


                saveAppearance.disabled = true;
                saveAppearance.textContent = "Saving...";


                try {

                    const result = await sendRequest(
                        "/admin/settings/appearance",
                        {
                            theme: selectedTheme.value
                        }
                    );


                    if (result.success) {

                        showMessage(
                            "appearanceMessage",
                            result.message,
                            true
                        );

                    }

                } catch (error) {

                    showMessage(
                        "appearanceMessage",
                        error.message,
                        false
                    );

                } finally {

                    saveAppearance.disabled = false;
                    saveAppearance.textContent =
                        "Save Appearance";

                }

            }
        );

    }

});