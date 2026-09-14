/* =========================================================
   STUDENT DASHBOARD JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PROFILE COMPLETION PROGRESS
       ===================================================== */

    const progressBar = document.querySelector(
        ".profile-progress-bar"
    );

    if (progressBar) {

        let progress = parseInt(
            progressBar.getAttribute("data-progress") || "0",
            10
        );

        /* Keep value safely between 0 and 100 */
        progress = Math.max(0, Math.min(100, progress));

        /* Small delay for smooth visual animation */
        setTimeout(function () {
            progressBar.style.width = progress + "%";
        }, 150);
    }


    /* =====================================================
       DASHBOARD ITEM HOVER ACCESSIBILITY
       ===================================================== */

    const dashboardItems = document.querySelectorAll(
        ".dashboard-application-item, " +
        ".dashboard-opportunity-item"
    );

    dashboardItems.forEach(function (item) {

        item.addEventListener("mouseenter", function () {
            item.classList.add("is-hovered");
        });

        item.addEventListener("mouseleave", function () {
            item.classList.remove("is-hovered");
        });

    });


    /* =====================================================
       DASHBOARD CARD KEYBOARD ACCESSIBILITY
       ===================================================== */

    const journeyLinks = document.querySelectorAll(
        ".journey-item > a"
    );

    journeyLinks.forEach(function (link) {

        link.addEventListener("keydown", function (event) {

            if (event.key === "Enter" || event.key === " ") {

                if (
                    link.getAttribute("href") === "#" &&
                    link.hasAttribute("data-coming-soon")
                ) {
                    event.preventDefault();

                    link.click();
                }

            }

        });

    });


    /* =====================================================
       DASHBOARD INITIALIZATION
       ===================================================== */

    document.body.classList.add(
        "student-dashboard-ready"
    );

});