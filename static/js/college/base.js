/* =========================================================
   SIH COLLEGE PORTAL
   COMMON COLLEGE JAVASCRIPT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {


        console.log(
            "SIH College Portal loaded successfully."
        );


        /* =================================================
           ELEMENTS
        ================================================= */

        const menuToggle =
            document.getElementById(
                "collegeMenuToggle"
            );


        const sidebar =
            document.getElementById(
                "collegeSidebar"
            );


        const sidebarClose =
            document.getElementById(
                "collegeSidebarClose"
            );


        const sidebarOverlay =
            document.getElementById(
                "collegeSidebarOverlay"
            );


        const logoutLink =
            document.getElementById(
                "collegeLogoutLink"
            );


        const notificationButton =
            document.getElementById(
                "collegeNotificationButton"
            );



        /* =================================================
           SIDEBAR — OPEN
        ================================================= */

        function openSidebar() {

            if (!sidebar) {
                return;
            }


            sidebar.classList.add(
                "open"
            );


            if (sidebarOverlay) {

                sidebarOverlay.classList.add(
                    "active"
                );

            }


            document.body.style.overflow =
                "hidden";
        }



        /* =================================================
           SIDEBAR — CLOSE
        ================================================= */

        function closeSidebar() {

            if (!sidebar) {
                return;
            }


            sidebar.classList.remove(
                "open"
            );


            if (sidebarOverlay) {

                sidebarOverlay.classList.remove(
                    "active"
                );

            }


            document.body.style.overflow =
                "";
        }



        /* =================================================
           MOBILE MENU BUTTON
        ================================================= */

        if (menuToggle) {

            menuToggle.addEventListener(
                "click",
                openSidebar
            );

        }



        /* =================================================
           SIDEBAR CLOSE BUTTON
        ================================================= */

        if (sidebarClose) {

            sidebarClose.addEventListener(
                "click",
                closeSidebar
            );

        }



        /* =================================================
           SIDEBAR OVERLAY
        ================================================= */

        if (sidebarOverlay) {

            sidebarOverlay.addEventListener(
                "click",
                closeSidebar
            );

        }



        /* =================================================
           CLOSE SIDEBAR AFTER NAVIGATION
        ================================================= */

        const navigationLinks =
            document.querySelectorAll(
                ".college-nav-item"
            );


        navigationLinks.forEach(
            function (link) {

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

            }
        );



        /* =================================================
           FLASH MESSAGE CLOSE
        ================================================= */

        const flashCloseButtons =
            document.querySelectorAll(
                ".college-flash-close"
            );


        flashCloseButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const flash =
                            button.closest(
                                ".college-flash"
                            );


                        if (flash) {

                            flash.style.opacity =
                                "0";

                            flash.style.transform =
                                "translateY(-5px)";

                            flash.style.transition =
                                "all 0.25s ease";


                            setTimeout(
                                function () {

                                    flash.remove();

                                },
                                250
                            );

                        }

                    }
                );

            }
        );



        /* =================================================
           AUTO HIDE FLASH MESSAGES
        ================================================= */

        setTimeout(
            function () {

                const flashMessages =
                    document.querySelectorAll(
                        ".college-flash"
                    );


                flashMessages.forEach(
                    function (flash) {

                        flash.style.opacity =
                            "0";

                        flash.style.transform =
                            "translateY(-5px)";

                        flash.style.transition =
                            "all 0.3s ease";


                        setTimeout(
                            function () {

                                if (
                                    flash &&
                                    flash.parentNode
                                ) {

                                    flash.remove();

                                }

                            },
                            300
                        );

                    }
                );

            },
            5000
        );



        /* =================================================
           LOGOUT CONFIRMATION
        ================================================= */

        if (logoutLink) {

            logoutLink.addEventListener(
                "click",
                function (event) {

                    const confirmLogout =
                        window.confirm(
                            "Are you sure you want to logout?"
                        );


                    if (!confirmLogout) {

                        event.preventDefault();

                    }

                }
            );

        }



        /* =================================================
           NOTIFICATION BUTTON
        ================================================= */

        if (notificationButton) {

            notificationButton.addEventListener(
                "click",
                function () {

                    /*
                     * Notification page/backend
                     * integration will be added
                     * in the Notifications phase.
                     */

                    console.log(
                        "College notifications clicked."
                    );

                }
            );

        }



        /* =================================================
           ACTIVE SIDEBAR ITEM
        ================================================= */

        const currentPath =
            window.location.pathname;


        navigationLinks.forEach(
            function (link) {

                const itemPath =
                    link.getAttribute("href");


                if (
                    !itemPath ||
                    itemPath === "#"
                ) {

                    return;

                }


                /*
                 * Dashboard exact match
                 */

                if (
                    itemPath ===
                    "/college/dashboard"
                ) {

                    if (
                        currentPath ===
                        "/college/dashboard"
                    ) {

                        link.classList.add(
                            "active"
                        );

                    }


                    return;

                }


                /*
                 * Other College sections
                 *
                 * Future routes will automatically
                 * work with this logic.
                 */

                if (
                    currentPath.startsWith(
                        itemPath
                    )
                ) {

                    link.classList.add(
                        "active"
                    );

                }

            }
        );



        /* =================================================
           WINDOW RESIZE
        ================================================= */

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



        /* =================================================
           ESCAPE KEY
        ================================================= */

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                ) {

                    closeSidebar();

                }

            }
        );


    }
);