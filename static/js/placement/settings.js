document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       ELEMENTS
    ===================================================== */

    const notificationForm =
        document.getElementById(
            "notificationSettingsForm"
        );

    const appearanceForm =
        document.getElementById(
            "appearanceSettingsForm"
        );

    const passwordForm =
        document.getElementById(
            "passwordSettingsForm"
        );

    const notificationBtn =
        document.getElementById(
            "saveNotificationBtn"
        );

    const appearanceBtn =
        document.getElementById(
            "saveAppearanceBtn"
        );

    const passwordBtn =
        document.getElementById(
            "changePasswordBtn"
        );

    const toast =
        document.getElementById(
            "settingsToast"
        );


    /* =====================================================
       TOAST
    ===================================================== */

    function showToast(message) {

        if (!toast) return;

        toast.textContent = message;

        toast.classList.add("show");

        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }


    /* =====================================================
       BUTTON LOADING
    ===================================================== */

    function setLoading(button, loading, text) {

        if (!button) return;

        if (loading) {

            button.dataset.originalText =
                button.textContent;

            button.disabled = true;
            button.textContent = text;

        } else {

            button.disabled = false;

            button.textContent =
                button.dataset.originalText ||
                text;
        }
    }


    /* =====================================================
       NOTIFICATION SETTINGS
    ===================================================== */

    if (notificationForm) {

        notificationForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                setLoading(
                    notificationBtn,
                    true,
                    "Saving..."
                );


                const formData =
                    new FormData();


                const messages =
                    notificationForm.querySelector(
                        '[name="notify_messages"]'
                    );

                const opportunities =
                    notificationForm.querySelector(
                        '[name="notify_opportunities"]'
                    );

                const collaborations =
                    notificationForm.querySelector(
                        '[name="notify_collaborations"]'
                    );


                formData.append(
                    "notify_messages",
                    messages && messages.checked
                        ? "true"
                        : "false"
                );

                formData.append(
                    "notify_opportunities",
                    opportunities && opportunities.checked
                        ? "true"
                        : "false"
                );

                formData.append(
                    "notify_collaborations",
                    collaborations && collaborations.checked
                        ? "true"
                        : "false"
                );


                try {

                    const response =
                        await fetch(
                            "{{ url_for('placement_update_notification_settings') }}",
                            {
                                method: "POST",
                                body: formData,
                                headers: {
                                    "X-Requested-With":
                                        "XMLHttpRequest"
                                }
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "Unable to save preferences."
                        );

                    }


                    showToast(
                        data.message ||
                        "Notification preferences saved."
                    );


                } catch (error) {

                    console.error(
                        "Notification settings error:",
                        error
                    );

                    showToast(
                        error.message ||
                        "Unable to save preferences."
                    );

                } finally {

                    setLoading(
                        notificationBtn,
                        false,
                        "Save Preferences"
                    );

                }

            }
        );
    }


    /* =====================================================
       APPEARANCE SETTINGS
    ===================================================== */

    if (appearanceForm) {

        appearanceForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                const selectedTheme =
                    appearanceForm.querySelector(
                        'input[name="theme"]:checked'
                    );


                if (!selectedTheme) {

                    showToast(
                        "Please select an appearance."
                    );

                    return;
                }


                setLoading(
                    appearanceBtn,
                    true,
                    "Saving..."
                );


                const formData =
                    new FormData();

                formData.append(
                    "theme",
                    selectedTheme.value
                );


                try {

                    const response =
                        await fetch(
                            "{{ url_for('placement_update_appearance') }}",
                            {
                                method: "POST",
                                body: formData,
                                headers: {
                                    "X-Requested-With":
                                        "XMLHttpRequest"
                                }
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "Unable to save appearance."
                        );

                    }


                    showToast(
                        data.message ||
                        "Appearance preference saved."
                    );


                    /*
                     * Apply theme immediately.
                     * Existing portal remains functional
                     * even if dark theme CSS is not globally
                     * implemented yet.
                     */

                    document.documentElement.dataset.theme =
                        selectedTheme.value;


                } catch (error) {

                    console.error(
                        "Appearance settings error:",
                        error
                    );

                    showToast(
                        error.message ||
                        "Unable to save appearance."
                    );

                } finally {

                    setLoading(
                        appearanceBtn,
                        false,
                        "Save Appearance"
                    );

                }

            }
        );
    }


    /* =====================================================
       PASSWORD
    ===================================================== */

    if (passwordForm) {

        passwordForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();


                const currentPassword =
                    document.getElementById(
                        "current_password"
                    );

                const newPassword =
                    document.getElementById(
                        "new_password"
                    );

                const confirmPassword =
                    document.getElementById(
                        "confirm_password"
                    );


                if (
                    !currentPassword ||
                    !newPassword ||
                    !confirmPassword
                ) {
                    return;
                }


                if (
                    newPassword.value.length < 6
                ) {

                    showToast(
                        "Password must be at least 6 characters."
                    );

                    newPassword.focus();

                    return;
                }


                if (
                    newPassword.value !==
                    confirmPassword.value
                ) {

                    showToast(
                        "New passwords do not match."
                    );

                    confirmPassword.focus();

                    return;
                }


                setLoading(
                    passwordBtn,
                    true,
                    "Changing..."
                );


                const formData =
                    new FormData(
                        passwordForm
                    );


                try {

                    const response =
                        await fetch(
                            "{{ url_for('placement_change_password') }}",
                            {
                                method: "POST",
                                body: formData,
                                headers: {
                                    "X-Requested-With":
                                        "XMLHttpRequest"
                                }
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "Unable to change password."
                        );

                    }


                    showToast(
                        data.message ||
                        "Password changed successfully."
                    );


                    passwordForm.reset();


                } catch (error) {

                    console.error(
                        "Password change error:",
                        error
                    );

                    showToast(
                        error.message ||
                        "Unable to change password."
                    );

                } finally {

                    setLoading(
                        passwordBtn,
                        false,
                        "Change Password"
                    );

                }

            }
        );
    }


    /* =====================================================
       PREVENT ACCIDENTAL DOUBLE SUBMIT
    ===================================================== */

    window.addEventListener(
        "beforeunload",
        () => {

            if (notificationBtn) {
                notificationBtn.disabled = false;
            }

            if (appearanceBtn) {
                appearanceBtn.disabled = false;
            }

            if (passwordBtn) {
                passwordBtn.disabled = false;
            }

        }
    );

});