/* =========================================================
   SIH ADMIN PORTAL
   PROJECT DETAILS JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    console.log(
        "SIH Admin Project Details JS loaded successfully."
    );


    /* =====================================================
       STATUS CONFIRMATION
       Future status/action handling can be added here.
       ===================================================== */

    const statusActions =
        document.querySelectorAll(".status-action");


    statusActions.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const confirmed =
                    confirm(
                        "Are you sure you want to change the project status?"
                    );


                if (!confirmed) {

                    event.preventDefault();

                }

            }
        );

    });

});