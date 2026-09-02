/* =========================================================
   SIH ADMIN PORTAL
   COLLEGE DETAILS JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       STATUS ACTION
       ===================================================== */

    const statusForm =
        document.querySelector(".status-form");


    const statusAction =
        document.getElementById("statusAction");


    if (statusForm && statusAction) {

        statusForm.addEventListener(
            "submit",
            function (event) {

                const buttonText =
                    statusAction.textContent
                        .trim()
                        .toLowerCase();


                let confirmationMessage;


                if (
                    buttonText.includes("deactivate")
                ) {

                    confirmationMessage =
                        "Are you sure you want to deactivate this college account?";

                } else {

                    confirmationMessage =
                        "Are you sure you want to activate this college account?";

                }


                const confirmed =
                    window.confirm(
                        confirmationMessage
                    );


                if (!confirmed) {

                    event.preventDefault();

                    return;

                }


                statusAction.disabled = true;

                statusAction.textContent =
                    "Updating...";

            }
        );

    }


    /* =====================================================
       EXTERNAL LINKS
       ===================================================== */

    const externalLinks =
        document.querySelectorAll(
            'a[target="_blank"]'
        );


    externalLinks.forEach(function (link) {

        link.setAttribute(
            "rel",
            "noopener noreferrer"
        );

    });


    /* =====================================================
       LOG
       ===================================================== */

    console.log(
        "SIH Admin College Details JS loaded successfully."
    );

});