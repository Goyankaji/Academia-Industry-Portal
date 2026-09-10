/* =========================================================
   PLACEMENT CELL BASE JS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       SIDEBAR TOGGLE
    ====================================================== */

    const sidebar = document.getElementById("placementSidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");

    if (sidebar && sidebarToggle) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("open");

        });

    }


    /* =====================================================
       COLLABORATION DROPDOWN
       ONLY COLLABORATION LOGIC
    ====================================================== */

    const collaborationToggle =
        document.getElementById("collaborationToggle");

    const collaborationSubmenu =
        document.getElementById("collaborationSubmenu");


    if (collaborationToggle && collaborationSubmenu) {

        collaborationToggle.addEventListener("click", function (event) {

            event.preventDefault();
            event.stopPropagation();

            const isOpen =
                collaborationSubmenu.classList.contains("open");


            if (isOpen) {

                collaborationSubmenu.classList.remove("open");

                collaborationToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            } else {

                collaborationSubmenu.classList.add("open");

                collaborationToggle.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }

        });


        /* -----------------------------------------------
           Keep submenu open on active collaboration page
        ------------------------------------------------ */

        const activeSubItem =
            collaborationSubmenu.querySelector(
                ".nav-subitem.active"
            );


        if (activeSubItem) {

            collaborationSubmenu.classList.add("open");

            collaborationToggle.setAttribute(
                "aria-expanded",
                "true"
            );

        }


        /* -----------------------------------------------
           Close when clicking outside dropdown
        ------------------------------------------------ */

        document.addEventListener("click", function (event) {

            const clickedInsideDropdown =
                event.target.closest(".nav-dropdown");


            if (!clickedInsideDropdown) {

                collaborationSubmenu.classList.remove("open");

                collaborationToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }

        });

    }


    /* =====================================================
       CLOSE SIDEBAR ON OUTSIDE CLICK
    ====================================================== */

    document.addEventListener("click", function (event) {

        if (
            window.innerWidth <= 850 &&
            sidebar &&
            sidebar.classList.contains("open")
        ) {

            const clickedInsideSidebar =
                sidebar.contains(event.target);

            const clickedToggle =
                sidebarToggle &&
                sidebarToggle.contains(event.target);

            if (!clickedInsideSidebar && !clickedToggle) {

                sidebar.classList.remove("open");

            }

        }

    });


    /* =====================================================
       AUTO DISMISS FLASH MESSAGES
    ====================================================== */

    const flashMessages =
        document.querySelectorAll(
            '.flash-message[data-auto-dismiss="true"]'
        );


    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transform = "translateY(-8px)";
            message.style.transition = "all 0.25s ease";

            setTimeout(function () {

                message.remove();

            }, 250);

        }, 4500);

    });


    /* =====================================================
       MANUAL FLASH CLOSE
    ====================================================== */

    const flashCloseButtons =
        document.querySelectorAll(".flash-close");


    flashCloseButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const flash =
                button.closest(".flash-message");

            if (flash) {

                flash.remove();

            }

        });

    });


    /* =====================================================
       CURRENT YEAR
    ====================================================== */

    const yearElements =
        document.querySelectorAll("[data-current-year]");


    yearElements.forEach(function (element) {

        element.textContent =
            new Date().getFullYear();

    });

});