document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       SETTINGS NAVIGATION
       ===================================================== */

    const navItems = document.querySelectorAll(
        ".settings-nav-item"
    );

    const sections = document.querySelectorAll(
        ".settings-section"
    );


    navItems.forEach(function (item) {

        item.addEventListener("click", function () {

            const targetSection =
                item.dataset.section;

            if (!targetSection) {
                return;
            }


            /* Remove active from navigation */

            navItems.forEach(function (nav) {
                nav.classList.remove("active");
            });


            /* Add active navigation */

            item.classList.add("active");


            /* Hide all sections */

            sections.forEach(function (section) {
                section.classList.remove("active");
            });


            /* Show selected section */

            const selectedSection =
                document.getElementById(
                    "settings-" + targetSection
                );

            if (selectedSection) {
                selectedSection.classList.add("active");
            }


            /* Keep section in URL without reload */

            if (window.history &&
                window.history.replaceState) {

                const url =
                    new URL(window.location.href);

                url.hash = targetSection;

                window.history.replaceState(
                    {},
                    "",
                    url
                );
            }

        });

    });



    /* =====================================================
       OPEN SECTION FROM URL HASH
       ===================================================== */

    const hash =
        window.location.hash.replace("#", "");

    if (hash) {

        const matchingNav =
            document.querySelector(
                '.settings-nav-item[data-section="' +
                hash +
                '"]'
            );

        if (matchingNav) {
            matchingNav.click();
        }

    }



    /* =====================================================
       PASSWORD SHOW / HIDE
       ===================================================== */

    const passwordToggles =
        document.querySelectorAll(
            ".password-toggle"
        );


    passwordToggles.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const targetId =
                    button.dataset.passwordTarget;

                const input =
                    document.getElementById(targetId);

                if (!input) {
                    return;
                }


                if (input.type === "password") {

                    input.type = "text";

                    button.textContent = "Hide";

                } else {

                    input.type = "password";

                    button.textContent = "Show";

                }

            }
        );

    });



    /* =====================================================
       PASSWORD VALIDATION
       ===================================================== */

    const passwordForm =
        document.getElementById(
            "passwordForm"
        );

    const passwordError =
        document.getElementById(
            "passwordError"
        );


    if (passwordForm) {

        passwordForm.addEventListener(
            "submit",
            function (event) {

                const currentPassword =
                    document.getElementById(
                        "currentPassword"
                    ).value.trim();

                const newPassword =
                    document.getElementById(
                        "newPassword"
                    ).value.trim();

                const confirmPassword =
                    document.getElementById(
                        "confirmPassword"
                    ).value.trim();


                let errorMessage = "";


                if (!currentPassword) {

                    errorMessage =
                        "Please enter your current password.";

                } else if (newPassword.length < 8) {

                    errorMessage =
                        "New password must contain at least 8 characters.";

                } else if (
                    newPassword !== confirmPassword
                ) {

                    errorMessage =
                        "New password and confirmation password do not match.";

                }


                if (errorMessage) {

                    event.preventDefault();

                    if (passwordError) {

                        passwordError.textContent =
                            errorMessage;

                        passwordError.style.display =
                            "block";
                    }

                    return;

                }


                if (passwordError) {

                    passwordError.textContent = "";

                    passwordError.style.display =
                        "none";
                }

            }
        );

    }



    /* =====================================================
       SETTINGS FORMS
       ===================================================== */

    const settingsForms =
        document.querySelectorAll(
            "[data-settings-form]"
        );


    settingsForms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                const button =
                    form.querySelector(
                        ".settings-primary-btn"
                    );

                if (!button) {
                    return;
                }


                button.dataset.originalText =
                    button.textContent;

                button.textContent =
                    "Saving...";

                button.disabled = true;


                /*
                 * Browser will continue normal form submission.
                 * The button is restored only if submission is
                 * interrupted by browser-side validation.
                 */

                window.setTimeout(
                    function () {

                        button.disabled = false;

                        if (button.dataset.originalText) {

                            button.textContent =
                                button.dataset.originalText;
                        }

                    },
                    3000
                );

            }
        );

    });



    /* =====================================================
       CONFIRMATION MODAL
       ===================================================== */

    const modal =
        document.getElementById(
            "settingsConfirmModal"
        );

    const modalTitle =
        document.getElementById(
            "settingsModalTitle"
        );

    const modalMessage =
        document.getElementById(
            "settingsModalMessage"
        );

    const closeModal =
        document.getElementById(
            "closeSettingsModal"
        );

    const cancelModal =
        document.getElementById(
            "cancelSettingsModal"
        );

    const confirmAction =
        document.getElementById(
            "confirmSettingsAction"
        );

    const deactivateButton =
        document.getElementById(
            "deactivateAccountBtn"
        );

    const deleteButton =
        document.getElementById(
            "deleteAccountBtn"
        );

    const logoutOtherSessions =
        document.getElementById(
            "logoutOtherSessions"
        );


    let currentAction = null;


    function openModal(
        title,
        message,
        action
    ) {

        if (!modal) {
            return;
        }

        modalTitle.textContent =
            title;

        modalMessage.textContent =
            message;

        currentAction =
            action;

        modal.classList.add("active");

        document.body.style.overflow =
            "hidden";
    }


    function hideModal() {

        if (!modal) {
            return;
        }

        modal.classList.remove(
            "active"
        );

        document.body.style.overflow =
            "";

        currentAction = null;
    }



    /* =====================================================
       DEACTIVATE ACCOUNT
       ===================================================== */

    if (deactivateButton) {

        deactivateButton.addEventListener(
            "click",
            function () {

                openModal(
                    "Deactivate Account?",
                    "Your Industry account will be disabled and you will no longer be able to access the portal until it is reactivated.",
                    "deactivate"
                );

            }
        );

    }



    /* =====================================================
       DELETE ACCOUNT
       ===================================================== */

    if (deleteButton) {

        deleteButton.addEventListener(
            "click",
            function () {

                openModal(
                    "Request Account Deletion?",
                    "This will submit a request to permanently remove your Industry account and associated portal data.",
                    "delete"
                );

            }
        );

    }



    /* =====================================================
       LOGOUT OTHER SESSIONS
       ===================================================== */

    if (logoutOtherSessions) {

        logoutOtherSessions.addEventListener(
            "click",
            function () {

                openModal(
                    "Log Out Other Sessions?",
                    "All other active sessions associated with your account will be signed out.",
                    "logout"
                );

            }
        );

    }



    /* =====================================================
       CONFIRM MODAL ACTION
       ===================================================== */

    if (confirmAction) {

        confirmAction.addEventListener(
            "click",
            function () {

                /*
                 * At this stage these actions are intentionally
                 * handled as UI confirmations.
                 *
                 * Backend endpoints can be connected here
                 * when the corresponding security/account
                 * routes are implemented.
                 */

                if (currentAction === "logout") {

                    hideModal();

                    window.alert(
                        "Other session management will be available after the session API is connected."
                    );

                    return;
                }


                if (currentAction === "deactivate") {

                    hideModal();

                    window.alert(
                        "Account deactivation request can be connected to the Industry account management endpoint."
                    );

                    return;
                }


                if (currentAction === "delete") {

                    hideModal();

                    window.alert(
                        "Account deletion request can be connected to the Industry account management endpoint."
                    );

                    return;
                }

            }
        );

    }



    /* =====================================================
       CLOSE MODAL
       ===================================================== */

    if (closeModal) {

        closeModal.addEventListener(
            "click",
            hideModal
        );

    }


    if (cancelModal) {

        cancelModal.addEventListener(
            "click",
            hideModal
        );

    }


    if (modal) {

        const overlay =
            modal.querySelector(
                ".settings-modal-overlay"
            );

        if (overlay) {

            overlay.addEventListener(
                "click",
                hideModal
            );

        }

    }


    /* =====================================================
       ESCAPE KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                modal.classList.contains("active")
            ) {

                hideModal();

            }

        }
    );



    /* =====================================================
       TOGGLE VISUAL FEEDBACK
       ===================================================== */

    const switches =
        document.querySelectorAll(
            ".settings-switch input"
        );


    switches.forEach(function (input) {

        input.addEventListener(
            "change",
            function () {

                const row =
                    input.closest(
                        ".settings-option-row"
                    );

                if (!row) {
                    return;
                }


                if (input.checked) {

                    row.classList.add(
                        "setting-enabled"
                    );

                } else {

                    row.classList.remove(
                        "setting-enabled"
                    );

                }

            }
        );

    });

});