document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PLACEMENT RATE BARS
    ===================================================== */

    const rateBars =
        document.querySelectorAll(".rate-bar");


    rateBars.forEach(function (bar) {

        const rawRate =
            bar.getAttribute("data-rate") || "0";

        let rate =
            parseFloat(rawRate);


        if (isNaN(rate)) {
            rate = 0;
        }


        /*
         * Keep percentage between 0 and 100.
         */

        rate = Math.max(
            0,
            Math.min(100, rate)
        );


        const fill =
            bar.querySelector("span");


        if (fill) {

            /*
             * Small delay gives the progress bar
             * a smooth animation when the page loads.
             */

            requestAnimationFrame(function () {

                fill.style.width =
                    rate + "%";

            });

        }

    });


    /* =====================================================
       BACK LINK
    ===================================================== */

    const backLinks =
        document.querySelectorAll(
            ".back-link"
        );


    backLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function (event) {

                const href =
                    this.getAttribute("href");

                if (!href || href === "#") {

                    event.preventDefault();

                    window.history.back();

                }

            }
        );

    });

});