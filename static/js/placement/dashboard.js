/* =========================================================
   PLACEMENT CELL DASHBOARD JS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       NUMBER COUNTERS
    ====================================================== */

    const counters =
        document.querySelectorAll(".counter");


    counters.forEach(function (counter) {

        const target =
            parseInt(
                counter.dataset.value || "0",
                10
            );


        if (target === 0) {

            counter.textContent = "0";

            return;
        }


        let current = 0;

        const duration = 650;

        const startTime = performance.now();


        function animateCounter(currentTime) {

            const elapsed =
                currentTime - startTime;

            const progress =
                Math.min(
                    elapsed / duration,
                    1
                );


            const eased =
                1 - Math.pow(
                    1 - progress,
                    3
                );


            current =
                Math.floor(
                    target * eased
                );


            counter.textContent =
                current.toLocaleString();


            if (progress < 1) {

                requestAnimationFrame(
                    animateCounter
                );

            } else {

                counter.textContent =
                    target.toLocaleString();

            }

        }


        requestAnimationFrame(
            animateCounter
        );

    });


    /* =====================================================
       APPLICATION PIPELINE
    ====================================================== */

    const pipelineBars =
        document.querySelectorAll(
            ".pipeline-progress"
        );


    pipelineBars.forEach(function (bar) {

        const count =
            parseInt(
                bar.dataset.count || "0",
                10
            );

        const total =
            parseInt(
                bar.dataset.total || "0",
                10
            );


        let percentage = 0;


        if (total > 0) {

            percentage =
                Math.min(
                    (count / total) * 100,
                    100
                );

        }


        setTimeout(function () {

            bar.style.width =
                percentage + "%";

        }, 150);

    });


    /* =====================================================
       REFRESH DASHBOARD
    ====================================================== */

    const refreshButton =
        document.querySelector(
            "[data-refresh-page]"
        );


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            function () {

                refreshButton.classList.add(
                    "spinning"
                );


                setTimeout(function () {

                    window.location.reload();

                }, 350);

            }
        );

    }


    /* =====================================================
       AUTO REFRESH
       Keep dashboard data reasonably fresh.
    ====================================================== */

    const AUTO_REFRESH_TIME =
        5 * 60 * 1000;


    let refreshTimer =
        setTimeout(function () {

            window.location.reload();

        }, AUTO_REFRESH_TIME);


    /* =====================================================
       CLEAR TIMER WHEN LEAVING PAGE
    ====================================================== */

    window.addEventListener(
        "beforeunload",
        function () {

            clearTimeout(refreshTimer);

        }
    );

});