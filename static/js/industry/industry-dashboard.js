/* =========================================================
   INDUSTRY DASHBOARD JS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log(
        "Industry Dashboard JS loaded."
    );


    /* =====================================================
       STAT CARD ANIMATION
    ====================================================== */

    const statCards =
        document.querySelectorAll(
            ".industry-stat-card"
        );


    statCards.forEach(
        function (card, index) {

            card.style.opacity = "0";
            card.style.transform =
                "translateY(8px)";


            setTimeout(
                function () {

                    card.style.transition =
                        "opacity 0.35s ease, transform 0.35s ease";

                    card.style.opacity = "1";
                    card.style.transform =
                        "translateY(0)";

                },
                index * 80
            );

        }
    );


    /* =====================================================
       PROFILE PROGRESS
    ====================================================== */

    const progressBar =
        document.querySelector(
            ".industry-progress-bar"
        );


    if (progressBar) {

            const progressValue =
                parseInt(
                    progressBar.getAttribute("data-progress") || "0",
                    10
                );

            const safeProgress =
                Math.min(
                    Math.max(progressValue, 0),
                    100
                );

            progressBar.style.width = "0%";

            setTimeout(
                function () {

                    progressBar.style.transition =
                        "width 0.8s ease";

                    progressBar.style.width =
                        safeProgress + "%";

                },
                300
            );

    }


    /* =====================================================
       QUICK ACTION FEEDBACK
    ====================================================== */

    const actionCards =
        document.querySelectorAll(
            ".industry-action-card"
        );


    actionCards.forEach(
        function (card) {

            card.addEventListener(
                "mouseenter",
                function () {

                    card.classList.add(
                        "action-hover"
                    );

                }
            );


            card.addEventListener(
                "mouseleave",
                function () {

                    card.classList.remove(
                        "action-hover"
                    );

                }
            );

        }
    );


    /* =====================================================
       DASHBOARD REFRESH HELPER
    ====================================================== */

    window.refreshIndustryDashboard =
        function () {

            /*
             * Backend/API refresh will be connected
             * here later if required.
             */

            console.log(
                "Industry dashboard refresh requested."
            );

        };

});