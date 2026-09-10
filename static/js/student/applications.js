/* =========================================================
   STUDENT APPLICATIONS JS
   ========================================================= */


document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =================================================
           DATE FORMATTING
           ================================================= */

        const dateElements =
            document.querySelectorAll(
                "[data-date]"
            );


        dateElements.forEach(
            function (element) {

                const rawDate =
                    element.dataset.date;


                if (
                    !rawDate ||
                    rawDate === "None" ||
                    rawDate === "null"
                ) {

                    return;

                }


                const date =
                    new Date(rawDate);


                if (
                    Number.isNaN(
                        date.getTime()
                    )
                ) {

                    return;

                }


                element.textContent =
                    date.toLocaleDateString(
                        "en-IN",
                        {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        }
                    );

            }
        );


        /* =================================================
           SEARCH ENTER
           ================================================= */

        const searchInput =
            document.getElementById(
                "applicationSearch"
            );


        if (searchInput) {

            searchInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();


                        if (
                            searchInput.form
                        ) {

                            searchInput.form.submit();

                        }

                    }

                }
            );

        }


        /* =================================================
           STATUS FILTER
           ================================================= */

        const statusFilter =
            document.getElementById(
                "applicationStatus"
            );


        if (statusFilter) {

            statusFilter.addEventListener(
                "change",
                function () {

                    const form =
                        document.getElementById(
                            "applicationFilterForm"
                        );


                    if (form) {

                        form.submit();

                    }

                }
            );

        }


        /* =================================================
           COPY APPLICATION ID
           ================================================= */

        const copyValues =
            document.querySelectorAll(
                ".copy-value"
            );


        copyValues.forEach(
            function (element) {

                element.addEventListener(
                    "click",
                    async function () {

                        const value =
                            element.dataset.copy;


                        if (!value) {

                            return;

                        }


                        try {

                            await navigator.clipboard.writeText(
                                value
                            );


                            const originalText =
                                element.textContent;


                            element.textContent =
                                "Copied ✓";


                            element.style.color =
                                "#166534";


                            setTimeout(
                                function () {

                                    element.textContent =
                                        originalText;

                                    element.style.color =
                                        "";

                                },
                                1200
                            );


                        } catch (error) {

                            console.log(
                                "Unable to copy application ID.",
                                error
                            );

                        }

                    }
                );

            }
        );


        /* =================================================
           APPLICATION CARD ANIMATION
           ================================================= */

        const applicationCards =
            document.querySelectorAll(
                ".application-card"
            );


        applicationCards.forEach(
            function (card, index) {

                card.style.opacity = "0";

                card.style.transform =
                    "translateY(6px)";


                setTimeout(
                    function () {

                        card.style.transition =
                            "opacity .25s ease, transform .25s ease";


                        card.style.opacity =
                            "1";


                        card.style.transform =
                            "translateY(0)";

                    },
                    Math.min(
                        index * 45,
                        300
                    )
                );

            }
        );


        /* =================================================
           DETAIL PAGE — SMOOTH SCROLL
           ================================================= */

        const detailSections =
            document.querySelectorAll(
                ".detail-section"
            );


        detailSections.forEach(
            function (section) {

                section.addEventListener(
                    "mouseenter",
                    function () {

                        section.classList.add(
                            "section-active"
                        );

                    }
                );


                section.addEventListener(
                    "mouseleave",
                    function () {

                        section.classList.remove(
                            "section-active"
                        );

                    }
                );

            }
        );

    }
);