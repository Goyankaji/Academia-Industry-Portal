/* =========================================================
   STUDENT PORTAL - BASE JS
   ========================================================= */


document.addEventListener("DOMContentLoaded", function () {

    const sidebar =
        document.getElementById("studentSidebar");

    const sidebarToggle =
        document.getElementById("sidebarToggle");


    /* =====================================================
       MOBILE SIDEBAR
       ===================================================== */

    if (sidebar && sidebarToggle) {

        sidebarToggle.addEventListener(
            "click",
            function () {

                sidebar.classList.toggle("open");

            }
        );

    }


    /* =====================================================
       AUTO HIDE FLASH MESSAGES
       ===================================================== */

    const alerts =
        document.querySelectorAll(
            ".student-alert"
        );


    alerts.forEach(function (alert) {

        setTimeout(function () {

            if (alert && alert.parentElement) {

                alert.remove();

            }

        }, 5000);

    });


});