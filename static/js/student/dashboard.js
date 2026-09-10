/* =========================================================
   STUDENT DASHBOARD JS
   ========================================================= */


document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       PROFILE COMPLETION
       ===================================================== */

    const progressBar =
        document.querySelector(".completion-fill");


    if (progressBar) {

        let progress =
            parseInt(
                progressBar.dataset.progress,
                10
            );


        /*
         * Safety check.
         * Progress should always remain between 0 and 100.
         */

        if (isNaN(progress)) {

            progress = 0;

        }


        progress =
            Math.max(
                0,
                Math.min(
                    100,
                    progress
                )
            );


        /*
         * Start from 0 so that the progress bar
         * animates when the dashboard loads.
         */

        progressBar.style.width = "0%";


        setTimeout(function () {

            progressBar.style.width =
                progress + "%";

        }, 150);

    }


    /* =====================================================
       STAT NUMBER ANIMATION
       ===================================================== */

    const statNumbers =
        document.querySelectorAll(
            ".stat-number"
        );


    statNumbers.forEach(function (element) {

        const target =
            parseInt(
                element.textContent.trim(),
                10
            );


        if (isNaN(target)) {

            return;

        }


        /*
         * Start from zero.
         */

        element.textContent = "0";


        let current = 0;


        const duration = 500;

        const steps = 25;

        const increment =
            target / steps;


        const interval =
            duration / steps;


        const counter =
            setInterval(function () {

                current += increment;


                if (current >= target) {

                    current = target;

                    clearInterval(counter);

                }


                element.textContent =
                    Math.round(current);

            }, interval);

    });


});