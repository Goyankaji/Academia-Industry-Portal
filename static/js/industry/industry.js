/* =========================================================
   INDUSTRY PORTAL - COMMON JS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("SIH Industry Portal loaded.");


    /* =====================================================
       SIDEBAR
    ====================================================== */

    const menuToggle =
        document.getElementById(
            "industryMenuToggle"
        );

    const sidebar =
        document.getElementById(
            "industrySidebar"
        );

    const sidebarClose =
        document.getElementById(
            "industrySidebarClose"
        );

    const sidebarOverlay =
        document.getElementById(
            "industrySidebarOverlay"
        );


    function openSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.add("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.add("active");
        }

        document.body.style.overflow = "hidden";
    }


    function closeSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.remove("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("active");
        }

        document.body.style.overflow = "";
    }


    if (menuToggle) {

        menuToggle.addEventListener(
            "click",
            openSidebar
        );

    }


    if (sidebarClose) {

        sidebarClose.addEventListener(
            "click",
            closeSidebar
        );

    }


    if (sidebarOverlay) {

        sidebarOverlay.addEventListener(
            "click",
            closeSidebar
        );

    }


    /* =====================================================
       CLOSE SIDEBAR AFTER NAVIGATION
    ====================================================== */

    const navigationLinks =
        document.querySelectorAll(
            ".industry-nav-item"
        );


    navigationLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                if (
                    window.innerWidth <= 1000
                ) {

                    closeSidebar();

                }

            }
        );

    });


    /* =====================================================
       FLASH MESSAGE CLOSE
    ====================================================== */

    const flashCloseButtons =
        document.querySelectorAll(
            ".industry-flash-close"
        );


    flashCloseButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const flash =
                        button.closest(
                            ".industry-flash"
                        );

                    if (flash) {

                        flash.remove();

                    }

                }
            );

        }
    );


    /* =====================================================
       AUTO HIDE FLASH MESSAGES
    ====================================================== */

    setTimeout(
        function () {

            const flashMessages =
                document.querySelectorAll(
                    ".industry-flash"
                );

            flashMessages.forEach(
                function (flash) {

                    flash.style.opacity = "0";

                    flash.style.transition =
                        "opacity 0.3s ease";

                    setTimeout(
                        function () {

                            flash.remove();

                        },
                        300
                    );

                }
            );

        },
        5000
    );


    /* =====================================================
       NOTIFICATION BUTTON
    ====================================================== */

    const notificationButton =
        document.getElementById(
            "industryNotificationButton"
        );


    if (notificationButton) {

        notificationButton.addEventListener(
            "click",
            function () {

                /*
                 * Notification page route will be
                 * connected in the Notifications phase.
                 *
                 * For now this button is intentionally
                 * kept ready for backend integration.
                 */

                console.log(
                    "Industry notifications clicked."
                );

            }
        );

    }


    /* =====================================================
       WINDOW RESIZE
    ====================================================== */

    window.addEventListener(
        "resize",
        function () {

            if (
                window.innerWidth > 1000
            ) {

                closeSidebar();

            }

        }
    );

});