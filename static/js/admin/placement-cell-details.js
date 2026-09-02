document.addEventListener("DOMContentLoaded", function () {

    const statusForms =
        document.querySelectorAll(
            'form[action*="/toggle-status"]'
        );


    statusForms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                const button =
                    form.querySelector(
                        'button[type="submit"]'
                    );

                const statusInput =
                    form.querySelector(
                        'input[name="status"]'
                    );

                if (!statusInput) {
                    return;
                }


                const newStatus =
                    statusInput.value;


                let message;


                if (newStatus === "ACTIVE") {

                    message =
                        "Are you sure you want to activate this placement cell?";

                } else {

                    message =
                        "Are you sure you want to deactivate this placement cell?";

                }


                if (!confirm(message)) {

                    event.preventDefault();

                    return;

                }


                if (button) {

                    button.disabled = true;

                    button.textContent =
                        newStatus === "ACTIVE"
                            ? "Activating..."
                            : "Deactivating...";

                }

            }
        );

    });

});