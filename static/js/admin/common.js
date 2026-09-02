/* =========================================================
   SIH ADMIN PORTAL
   COMMON ADMIN JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const mobileMenuBtn =
        document.getElementById("mobileMenuBtn");

    const sidebar =
        document.getElementById("adminSidebar");

    const sidebarClose =
        document.getElementById("sidebarClose");

    const sidebarOverlay =
        document.getElementById("sidebarOverlay");


    const notificationBtn =
        document.getElementById("notificationBtn");

    const notificationDropdown =
        document.getElementById("notificationDropdown");


    const adminProfileBtn =
        document.getElementById("adminProfileBtn");

    const profileDropdown =
        document.getElementById("profileDropdown");


    const logoutLink =
        document.getElementById("logoutLink");


    /* =====================================================
       MOBILE SIDEBAR
       ===================================================== */

    function openSidebar() {

        if (!sidebar) return;

        sidebar.classList.add("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.add("show");
        }

        document.body.style.overflow = "hidden";
    }


    function closeSidebar() {

        if (!sidebar) return;

        sidebar.classList.remove("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("show");
        }

        document.body.style.overflow = "";
    }


    if (mobileMenuBtn) {

        mobileMenuBtn.addEventListener(
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
       CLOSE SIDEBAR AFTER NAVIGATION — MOBILE
       ===================================================== */

    const navItems =
        document.querySelectorAll(".nav-item");

    navItems.forEach(function (item) {

        item.addEventListener("click", function () {

            if (window.innerWidth <= 768) {
                closeSidebar();
            }

        });

    });


    /* =====================================================
       NOTIFICATION DROPDOWN
       ===================================================== */

    if (notificationBtn &&
        notificationDropdown) {

        notificationBtn.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                notificationDropdown
                    .classList.toggle("show");

                if (profileDropdown) {
                    profileDropdown
                        .classList.remove("show");
                }

            }
        );
    }


    /* =====================================================
       ADMIN PROFILE DROPDOWN
       ===================================================== */

    if (adminProfileBtn &&
        profileDropdown) {

        adminProfileBtn.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                profileDropdown
                    .classList.toggle("show");

                if (notificationDropdown) {
                    notificationDropdown
                        .classList.remove("show");
                }

            }
        );
    }


    /* =====================================================
       CLOSE DROPDOWNS WHEN CLICKING OUTSIDE
       ===================================================== */

    document.addEventListener(
        "click",
        function () {

            if (notificationDropdown) {

                notificationDropdown
                    .classList.remove("show");
            }


            if (profileDropdown) {

                profileDropdown
                    .classList.remove("show");
            }

        }
    );


    /* =====================================================
       PREVENT DROPDOWN FROM CLOSING
       ===================================================== */

    if (notificationDropdown) {

        notificationDropdown.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

            }
        );
    }


    if (profileDropdown) {

        profileDropdown.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

            }
        );
    }


    /* =====================================================
       LOGOUT CONFIRMATION
       ===================================================== */

    if (logoutLink) {

        logoutLink.addEventListener(
            "click",
            function (event) {

                const confirmLogout =
                    confirm(
                        "Are you sure you want to logout?"
                    );


                if (!confirmLogout) {

                    event.preventDefault();

                }

            }
        );
    }


    /* =====================================================
       HANDLE WINDOW RESIZE
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
       ACTIVE SIDEBAR ITEM
       ===================================================== */

    const currentPath =
        window.location.pathname;

    navItems.forEach(function (item) {

        const itemPath =
            item.getAttribute("href");

        if (!itemPath) return;


        /*
         * Dashboard exact match
         */

        if (itemPath === "/admin/dashboard") {

            if (currentPath === "/admin/dashboard") {

                item.classList.add("active");

            }

            return;
        }


        /*
         * Other admin sections
         */

        if (
            currentPath.startsWith(itemPath) &&
            itemPath !== "/admin/dashboard"
        ) {

            item.classList.add("active");

        }

    });


    /* =====================================================
       CONSOLE MESSAGE
       ===================================================== */

    console.log(
        "SIH Admin Common JS loaded successfully."
    );

});