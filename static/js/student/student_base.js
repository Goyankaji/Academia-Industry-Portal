/* =========================================================
   SIH STUDENT PORTAL
   Common Student Base JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
    ===================================================== */

    const sidebar = document.getElementById("studentSidebar");
    const sidebarToggleBtn = document.getElementById("sidebarToggleBtn");
    const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");

    const notificationBtn = document.getElementById("notificationBtn");
    const notificationDropdown =
        document.getElementById("notificationDropdown");

    const markAllReadBtn =
        document.getElementById("markAllNotificationsRead");


    /* =====================================================
       MOBILE SIDEBAR
    ===================================================== */

    function openSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.add("mobile-open");

        if (sidebarToggleBtn) {
            sidebarToggleBtn.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        createSidebarOverlay();

    }


    function closeSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.remove("mobile-open");

        if (sidebarToggleBtn) {
            sidebarToggleBtn.setAttribute(
                "aria-expanded",
                "false"
            );
        }

        removeSidebarOverlay();

    }


    if (sidebarToggleBtn) {

        sidebarToggleBtn.addEventListener(
            "click",
            function () {

                if (sidebar.classList.contains("mobile-open")) {
                    closeSidebar();
                } else {
                    openSidebar();
                }

            }
        );

    }


    if (sidebarCloseBtn) {

        sidebarCloseBtn.addEventListener(
            "click",
            function () {
                closeSidebar();
            }
        );

    }


    /* =====================================================
       SIDEBAR OVERLAY
    ===================================================== */

    function createSidebarOverlay() {

        let overlay =
            document.querySelector(".student-sidebar-overlay");

        if (!overlay) {

            overlay =
                document.createElement("div");

            overlay.className =
                "student-sidebar-overlay";

            document.body.appendChild(overlay);

            overlay.addEventListener(
                "click",
                closeSidebar
            );

        }

        requestAnimationFrame(function () {

            overlay.classList.add("active");

        });

    }


    function removeSidebarOverlay() {

        const overlay =
            document.querySelector(".student-sidebar-overlay");

        if (!overlay) {
            return;
        }

        overlay.classList.remove("active");

        setTimeout(function () {

            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }

        }, 250);

    }


    /* =====================================================
       CLOSE SIDEBAR ON NAVIGATION
    ===================================================== */

    const navItems =
        document.querySelectorAll(
            ".student-nav-item"
        );


    navItems.forEach(function (item) {

        item.addEventListener(
            "click",
            function () {

                if (
                    window.innerWidth <= 768 &&
                    !item.classList.contains("coming-soon")
                ) {

                    closeSidebar();

                }

            }
        );

    });


    /* =====================================================
       COMING SOON ITEMS
    ===================================================== */

    const comingSoonItems =
        document.querySelectorAll(
            "[data-coming-soon='true']"
        );


    comingSoonItems.forEach(function (item) {

        item.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showStudentToast(
                    "This section will be available soon."
                );

            }
        );

    });


    /* =====================================================
       NOTIFICATION DROPDOWN
    ===================================================== */

    function openNotificationDropdown() {

        if (!notificationDropdown) {
            return;
        }

        notificationDropdown.classList.add("show");

        notificationDropdown.setAttribute(
            "aria-hidden",
            "false"
        );

        if (notificationBtn) {

            notificationBtn.setAttribute(
                "aria-expanded",
                "true"
            );

        }

    }


    function closeNotificationDropdown() {

        if (!notificationDropdown) {
            return;
        }

        notificationDropdown.classList.remove("show");

        notificationDropdown.setAttribute(
            "aria-hidden",
            "true"
        );

        if (notificationBtn) {

            notificationBtn.setAttribute(
                "aria-expanded",
                "false"
            );

        }

    }


    if (notificationBtn) {

        notificationBtn.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                if (
                    notificationDropdown &&
                    notificationDropdown.classList.contains("show")
                ) {

                    closeNotificationDropdown();

                } else {

                    openNotificationDropdown();

                }

            }
        );

    }


    /* =====================================================
       CLOSE DROPDOWN WHEN CLICKING OUTSIDE
    ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (!notificationDropdown) {
                return;
            }

            const wrapper =
                document.querySelector(
                    ".topbar-notification-wrapper"
                );

            if (
                wrapper &&
                !wrapper.contains(event.target)
            ) {

                closeNotificationDropdown();

            }

        }
    );


    /* =====================================================
       ESC KEY
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key !== "Escape") {
                return;
            }

            closeNotificationDropdown();
            closeSidebar();

        }
    );


    /* =====================================================
       WINDOW RESIZE
    ===================================================== */

    window.addEventListener(
        "resize",
        function () {

            if (window.innerWidth > 768) {
                closeSidebar();
            }

        }
    );


    /* =====================================================
       SKILL PROGRESS BARS
    ===================================================== */

    const progressBars =
        document.querySelectorAll(
            ".skill-progress-fill[data-progress]"
        );


    progressBars.forEach(function (bar) {

        let progress =
            parseInt(
                bar.getAttribute("data-progress"),
                10
            );


        if (isNaN(progress)) {
            progress = 0;
        }


        progress =
            Math.max(
                0,
                Math.min(100, progress)
            );


        requestAnimationFrame(function () {

            bar.style.width =
                progress + "%";

        });

    });


    /* =====================================================
       MARK ALL NOTIFICATIONS AS READ
       
       NOTE:
       Actual database update will be connected
       during Phase 9 Notification Integration.
    ===================================================== */

    if (markAllReadBtn) {

        markAllReadBtn.addEventListener(
            "click",
            function () {

                const unreadItems =
                    document.querySelectorAll(
                        ".notification-item.unread"
                    );


                unreadItems.forEach(
                    function (item) {

                        item.classList.remove("unread");

                        const dot =
                            item.querySelector(
                                ".notification-unread-dot"
                            );

                        if (dot) {
                            dot.remove();
                        }

                    }
                );


                const countText =
                    document.querySelector(
                        ".notification-count-text"
                    );


                if (countText) {

                    countText.textContent =
                        "You're all caught up";

                }


                markAllReadBtn.remove();


                showStudentToast(
                    "Notifications marked as read."
                );

            }
        );

    }


    /* =====================================================
       SIMPLE STUDENT TOAST
    ===================================================== */

    function showStudentToast(message) {

        let toast =
            document.querySelector(
                ".student-toast"
            );


        if (!toast) {

            toast =
                document.createElement("div");

            toast.className =
                "student-toast";

            document.body.appendChild(toast);

        }


        toast.textContent = message;

        toast.classList.add("show");


        setTimeout(function () {

            toast.classList.remove("show");

        }, 2500);

    }


    /* =====================================================
       INITIAL STATE
    ===================================================== */

    if (notificationDropdown) {

        notificationDropdown.setAttribute(
            "aria-hidden",
            "true"
        );

    }


    if (sidebarToggleBtn) {

        sidebarToggleBtn.setAttribute(
            "aria-expanded",
            "false"
        );

    }


});