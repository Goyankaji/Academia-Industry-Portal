document.addEventListener("DOMContentLoaded", function () {

    console.log(
        "Student Notifications JS loaded successfully."
    );


    /* =====================================================
       BUTTON FEEDBACK
    ===================================================== */

    const forms =
        document.querySelectorAll(
            ".mark-all-form, .notification-item form"
        );


    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                const button =
                    form.querySelector("button");

                if (!button) {
                    return;
                }

                button.disabled = true;

                const originalText =
                    button.textContent;

                button.textContent =
                    "Updating...";


                setTimeout(function () {

                    if (button.disabled) {

                        button.textContent =
                            originalText;

                    }

                }, 5000);

            }
        );

    });



    /* =====================================================
       SEARCH ENTER SUPPORT
    ===================================================== */

    const searchInput =
        document.querySelector(
            ".notification-search-box input"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    const form =
                        searchInput.closest("form");

                    if (form) {
                        form.submit();
                    }

                }

            }
        );

    }



    /* =====================================================
       CLEAR SEARCH WITH ESC
    ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape" &&
                    searchInput.value
                ) {

                    searchInput.value = "";

                }

            }
        );

    }

});