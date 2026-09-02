/* =========================================================
   SIH ADMIN PORTAL
   STUDENT DETAILS JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       STATUS ACTION CONFIRMATION
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
                        "Are you sure you want to deactivate this student account?";

                } else {

                    confirmationMessage =
                        "Are you sure you want to activate this student account?";

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
       EXTERNAL LINK SAFETY
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
        "SIH Admin Student Details JS loaded successfully."
    );

});