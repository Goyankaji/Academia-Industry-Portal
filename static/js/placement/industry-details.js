document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       EXTERNAL WEBSITE LINK
    ===================================================== */

    const websiteLinks =
        document.querySelectorAll(
            'a[target="_blank"]'
        );

    websiteLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                /*
                 * External company website intentionally
                 * opens in a new tab.
                 */

            }
        );

    });


    /* =====================================================
       BACK BUTTON
    ===================================================== */

    const backButtons =
        document.querySelectorAll(
            ".back-link, .back-button"
        );

    backButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const href =
                    this.getAttribute("href");

                /*
                 * Normal Flask URL navigation is preferred.
                 * History fallback is only used if there
                 * is no valid href.
                 */

                if (!href || href === "#") {

                    event.preventDefault();

                    window.history.back();

                }

            }
        );

    });


    /* =====================================================
       OPPORTUNITY / COLLABORATION HOVER
    ===================================================== */

    const items =
        document.querySelectorAll(
            ".opportunity-item, .collaboration-item"
        );

    items.forEach(function (item) {

        item.addEventListener(
            "mouseenter",
            function () {

                this.style.transition =
                    "background-color 0.15s ease";

                this.style.backgroundColor =
                    "#f8fafc";

            }
        );


        item.addEventListener(
            "mouseleave",
            function () {

                this.style.backgroundColor =
                    "#fafbfc";

            }
        );

    });

});