document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // PROGRESS BAR INITIALIZATION
    // =====================================================

    const progressBars = document.querySelectorAll(
        "[data-progress]"
    );

    progressBars.forEach(function (bar) {

        let progress = parseFloat(
            bar.getAttribute("data-progress")
        );

        if (isNaN(progress)) {
            progress = 0;
        }

        progress = Math.max(
            0,
            Math.min(100, progress)
        );

        bar.style.width = progress + "%";
    });


    // =====================================================
    // DEFAULT PROGRESS DATE
    // =====================================================

    const progressDate = document.getElementById(
        "progress_date"
    );

    if (progressDate && !progressDate.value) {

        const today = new Date();

        const year = today.getFullYear();

        const month = String(
            today.getMonth() + 1
        ).padStart(2, "0");

        const day = String(
            today.getDate()
        ).padStart(2, "0");

        progressDate.value =
            `${year}-${month}-${day}`;
    }


    // =====================================================
    // FORM ELEMENTS
    // =====================================================

    const form = document.getElementById(
        "internshipProgressForm"
    );

    const percentageInput = document.getElementById(
        "progress_percentage"
    );

    const statusInput = document.getElementById(
        "status"
    );

    const submitButton = document.getElementById(
        "progressSubmitBtn"
    );


    // =====================================================
    // AUTO UPDATE STATUS
    // =====================================================

    if (percentageInput && statusInput) {

        percentageInput.addEventListener(
            "input",
            function () {

                let value = parseFloat(
                    percentageInput.value
                );

                if (isNaN(value)) {
                    return;
                }

                if (value < 0) {
                    percentageInput.value = 0;
                    value = 0;
                }

                if (value > 100) {
                    percentageInput.value = 100;
                    value = 100;
                }

                if (value >= 100) {

                    statusInput.value =
                        "COMPLETED";

                } else if (value > 0) {

                    statusInput.value =
                        "IN_PROGRESS";

                }

            }
        );
    }


    // =====================================================
    // FORM VALIDATION
    // =====================================================

    if (form) {

        form.addEventListener(
            "submit",
            function (event) {

                const title =
                    document.getElementById("title");

                const description =
                    document.getElementById("description");

                const date =
                    document.getElementById(
                        "progress_date"
                    );

                const percentage =
                    document.getElementById(
                        "progress_percentage"
                    );

                if (!title || !title.value.trim()) {

                    event.preventDefault();

                    alert(
                        "Please enter a progress title."
                    );

                    if (title) {
                        title.focus();
                    }

                    return;
                }


                if (!date || !date.value) {

                    event.preventDefault();

                    alert(
                        "Please select the progress date."
                    );

                    if (date) {
                        date.focus();
                    }

                    return;
                }


                const progressValue =
                    parseFloat(
                        percentage.value
                    );

                if (
                    isNaN(progressValue) ||
                    progressValue < 0 ||
                    progressValue > 100
                ) {

                    event.preventDefault();

                    alert(
                        "Progress percentage must be between 0 and 100."
                    );

                    percentage.focus();

                    return;
                }


                // -----------------------------------------
                // PREVENT DOUBLE SUBMISSION
                // -----------------------------------------

                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.textContent =
                        "Saving Progress...";
                }

            }
        );
    }


    // =====================================================
    // HISTORY ANIMATION
    // =====================================================

    const historyItems =
        document.querySelectorAll(
            ".internship-progress-history-item"
        );

    historyItems.forEach(
        function (item, index) {

            item.style.opacity = "0";

            item.style.transform =
                "translateY(10px)";

            setTimeout(
                function () {

                    item.style.transition =
                        "opacity 0.35s ease, transform 0.35s ease";

                    item.style.opacity = "1";

                    item.style.transform =
                        "translateY(0)";

                },
                index * 80
            );

        }
    );


    // =====================================================
    // DESCRIPTION CHARACTER FEEDBACK
    // =====================================================

    const description =
        document.getElementById("description");

    if (description) {

        description.addEventListener(
            "input",
            function () {

                if (description.value.length > 2000) {

                    description.value =
                        description.value.substring(
                            0,
                            2000
                        );
                }

            }
        );
    }

});