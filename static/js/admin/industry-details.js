/* =========================================================
   SIH ADMIN PORTAL
   INDUSTRY DETAILS JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       STATUS FORM
       ===================================================== */

    const statusForm =
        document.querySelector(".status-form");


    if (statusForm) {

        statusForm.addEventListener(
            "submit",
            function (event) {

                const button =
                    statusForm.querySelector("button");

                const hiddenStatus =
                    statusForm.querySelector(
                        'input[name="status"]'
                    );


                if (!hiddenStatus) {
                    return;
                }


                const newStatus =
                    hiddenStatus.value;


                const actionText =
                    newStatus === "ACTIVE"
                        ? "activate"
                        : "deactivate";


                const confirmed =
                    confirm(
                        `Are you sure you want to ${actionText} this industry?`
                    );


                if (!confirmed) {

                    event.preventDefault();

                    return;

                }


                if (button) {

                    button.disabled = true;

                    button.style.opacity = "0.6";

                }

            }
        );

    }


    console.log(
        "SIH Admin Industry Details JS loaded successfully."
    );

});