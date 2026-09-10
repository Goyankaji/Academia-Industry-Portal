document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       BACK BUTTON
    ===================================================== */

    const backButtons = document.querySelectorAll(
        ".back-link, .back-button"
    );

    backButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const href =
                    this.getAttribute("href");

                /*
                 * Let normal Flask URL navigation happen.
                 * Only use browser history if no href exists.
                 */

                if (!href || href === "#") {

                    event.preventDefault();

                    window.history.back();

                }

            }
        );

    });


    /* =====================================================
       EXTERNAL PROFILE LINKS
    ===================================================== */

    const externalLinks =
        document.querySelectorAll(
            '.profile-links a[target="_blank"]'
        );

    externalLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                /*
                 * External links intentionally open
                 * in a new tab.
                 */

            }
        );

    });

});