/* =========================================================
   SIH ADMIN PORTAL
   USER DETAILS JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    const statusForms =
        document.querySelectorAll(".status-form");


    statusForms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                const button =
                    form.querySelector("button");


                if (button) {

                    button.disabled = true;

                    button.style.opacity = "0.65";

                }

            }
        );

    });


    console.log(
        "SIH Admin User Details JS loaded successfully."
    );

});