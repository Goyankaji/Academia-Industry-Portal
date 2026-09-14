document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // PORTFOLIO EDITOR ELEMENTS
    // =====================================================

    const modal =
        document.getElementById("portfolioEditor");

    const openButton =
        document.getElementById("openPortfolioEditor");

    const closeButton =
        document.getElementById("closePortfolioEditor");

    const cancelButton =
        document.getElementById("cancelPortfolioEditor");


    // =====================================================
    // OPEN PORTFOLIO EDITOR
    // =====================================================

    function openPortfolioEditor() {

        if (!modal) {
            return;
        }

        modal.hidden = false;

        document.body.classList.add(
            "modal-open"
        );
    }


    // =====================================================
    // CLOSE PORTFOLIO EDITOR
    // =====================================================

    function closePortfolioEditor() {

        if (!modal) {
            return;
        }

        modal.hidden = true;

        document.body.classList.remove(
            "modal-open"
        );
    }


    // =====================================================
    // OPEN BUTTON
    // =====================================================

    if (openButton) {

        openButton.addEventListener(
            "click",
            openPortfolioEditor
        );

    }


    // =====================================================
    // CLOSE BUTTON
    // =====================================================

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closePortfolioEditor
        );

    }


    // =====================================================
    // CANCEL BUTTON
    // =====================================================

    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            closePortfolioEditor
        );

    }


    // =====================================================
    // CLICK OUTSIDE MODAL
    // =====================================================

    if (modal) {

        modal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === modal
                ) {

                    closePortfolioEditor();

                }

            }
        );

    }


    // =====================================================
    // ESCAPE KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal &&
                !modal.hidden
            ) {

                closePortfolioEditor();

            }

        }
    );


    // =====================================================
    // PUBLIC SLUG INPUT
    // =====================================================

    const slugInput =
        document.querySelector(
            'input[name="public_slug"]'
        );


    if (slugInput) {

        slugInput.addEventListener(
            "input",
            function () {

                let value = this.value;

                // Convert to lowercase
                value = value.toLowerCase();

                // Replace invalid characters
                value = value.replace(
                    /[^a-z0-9-]/g,
                    "-"
                );

                // Remove multiple hyphens
                value = value.replace(
                    /-+/g,
                    "-"
                );

                // Remove hyphen from beginning
                value = value.replace(
                    /^-+/,
                    ""
                );

                // Remove hyphen from end
                value = value.replace(
                    /-+$/,
                    ""
                );

                // Maximum 150 characters
                value = value.substring(
                    0,
                    150
                );

                this.value = value;

            }
        );

    }


    // =====================================================
    // SKILL PROGRESS BARS
    // =====================================================

    const progressBars =
        document.querySelectorAll(
            ".skill-progress-bar"
        );


    progressBars.forEach(
        function (bar) {

            let progress =
                parseFloat(
                    bar.dataset.progress
                );


            // If invalid value
            if (isNaN(progress)) {

                progress = 0;

            }


            // Keep percentage between 0 and 100
            progress =
                Math.max(
                    0,
                    Math.min(
                        100,
                        progress
                    )
                );


            // Set width
            bar.style.width =
                progress + "%";

        }
    );


    // =====================================================
    // PREVENT BODY SCROLL WHEN MODAL IS OPEN
    // =====================================================

    function updateBodyScroll() {

        if (
            modal &&
            !modal.hidden
        ) {

            document.body.style.overflow =
                "hidden";

        } else {

            document.body.style.overflow =
                "";

        }

    }


    // =====================================================
    // OBSERVE MODAL STATE
    // =====================================================

    if (modal) {

        const observer =
            new MutationObserver(
                function () {

                    updateBodyScroll();

                }
            );


        observer.observe(
            modal,
            {
                attributes: true,
                attributeFilter: ["hidden"]
            }
        );

    }


    // =====================================================
    // INITIALIZE
    // =====================================================

    updateBodyScroll();

});