/* =========================================================
   SIH ADMIN PORTAL
   DASHBOARD JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const refreshButton =
        document.getElementById("refreshDashboard");


    /* =====================================================
       REFRESH DASHBOARD
       ===================================================== */

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            function () {

                /*
                 * The dashboard data is loaded by Flask
                 * from MySQL whenever the page loads.
                 *
                 * Therefore, refreshing the page will
                 * execute all dashboard queries again.
                 */

                refreshButton.classList.add("loading");

                refreshButton.disabled = true;


                /*
                 * Small delay so the refresh animation
                 * is visible to the user.
                 */

                setTimeout(function () {

                    window.location.reload();

                }, 400);

            }
        );

    }


    /* =====================================================
       STAT CARD NUMBER ANIMATION
       ===================================================== */

    const statValues =
        document.querySelectorAll(".stat-value");


    statValues.forEach(function (element) {

        const finalValue =
            parseInt(
                element.textContent.trim(),
                10
            );


        if (isNaN(finalValue)) {
            return;
        }


        /*
         * Do not animate very large numbers too slowly.
         */

        const duration = 500;

        const startTime =
            performance.now();


        function animateNumber(currentTime) {

            const elapsed =
                currentTime - startTime;

            const progress =
                Math.min(
                    elapsed / duration,
                    1
                );


            /*
             * Ease-out animation
             */

            const easedProgress =
                1 - Math.pow(
                    1 - progress,
                    3
                );


            const currentValue =
                Math.floor(
                    finalValue *
                    easedProgress
                );


            element.textContent =
                currentValue.toLocaleString();


            if (progress < 1) {

                requestAnimationFrame(
                    animateNumber
                );

            } else {

                element.textContent =
                    finalValue.toLocaleString();

            }

        }


        /*
         * Only animate if value is greater than zero.
         */

        if (finalValue > 0) {

            element.textContent = "0";

            requestAnimationFrame(
                animateNumber
            );

        }

    });


    /* =====================================================
       QUICK ACTION KEYBOARD SUPPORT
       ===================================================== */

    const quickActions =
        document.querySelectorAll(
            ".quick-action"
        );


    quickActions.forEach(function (action) {

        action.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();

                    action.click();

                }

            }
        );

    });


    /* =====================================================
       DASHBOARD LOADED
       ===================================================== */

    console.log(
        "SIH Admin Dashboard loaded successfully."
    );

});