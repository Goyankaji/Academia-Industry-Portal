document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // SKILL MATCH PROGRESS BAR
    // =====================================================

    const progressBar =
        document.querySelector(".detail-progress-fill");

    if (progressBar) {

        let percentage =
            parseFloat(
                progressBar.dataset.width || "0"
            );

        if (percentage < 0) {
            percentage = 0;
        }

        if (percentage > 100) {
            percentage = 100;
        }

        setTimeout(function () {

            progressBar.style.width =
                percentage + "%";

        }, 100);
    }


    // =====================================================
    // APPLY BUTTON FEEDBACK
    // =====================================================

    const applyButton =
        document.querySelector(".detail-apply-btn");

    if (applyButton) {

        applyButton.addEventListener(
            "click",
            function () {

                if (applyButton.getAttribute("href") === "#") {

                    applyButton.classList.add("loading");

                }

            }
        );

    }

});