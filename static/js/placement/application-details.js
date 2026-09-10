document.addEventListener("DOMContentLoaded", function () {

    /*
     * Back navigation
     */

    const backButtons = document.querySelectorAll(
        ".back-link, .back-button"
    );

    backButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            /*
             * Normal anchor navigation is preferred.
             * This handler only provides browser-history
             * fallback when appropriate.
             */

            const href = this.getAttribute("href");

            if (!href) {
                event.preventDefault();
                window.history.back();
            }

        });

    });

    /*
     * External student profile links
     * are already handled through target="_blank".
     */

});