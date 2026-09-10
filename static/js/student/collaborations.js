/* =========================================================
   STUDENT COLLABORATIONS JS
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
                "collaborationSearch"
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
                "collaborationStatus"
            );


        if (statusFilter) {

            statusFilter.addEventListener(
                "change",
                function () {

                    const form =
                        document.getElementById(
                            "collaborationFilterForm"
                        );


                    if (form) {

                        form.submit();

                    }

                }
            );

        }



        /* =================================================
           TYPE FILTER
           ================================================= */

        const typeFilter =
            document.getElementById(
                "collaborationType"
            );


        if (typeFilter) {

            typeFilter.addEventListener(
                "change",
                function () {

                    const form =
                        document.getElementById(
                            "collaborationFilterForm"
                        );


                    if (form) {

                        form.submit();

                    }

                }
            );

        }



        /* =================================================
           CARD ANIMATION
           ================================================= */

        const cards =
            document.querySelectorAll(
                ".collaboration-card"
            );


        cards.forEach(
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
           WEBSITE LINK
           ================================================= */

        const websiteLinks =
            document.querySelectorAll(
                ".website-btn"
            );


        websiteLinks.forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function () {

                        link.style.opacity =
                            "0.65";

                    }
                );

            }
        );

    }
);