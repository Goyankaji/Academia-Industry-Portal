/* =========================================================
   SIH PORTAL - REGISTRATION SELECTION JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const registrationOptions =
        document.querySelectorAll(
            ".registration-option"
        );


    /* =====================================================
       ROLE OPTION INTERACTION
       ===================================================== */

    registrationOptions.forEach(function (option) {

        option.addEventListener(
            "keydown",
            function (event) {

                /*
                 * Allow Enter and Space to activate
                 * the registration option.
                 */

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();

                    option.click();

                }

            }
        );

    });

});