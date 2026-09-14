document.addEventListener("DOMContentLoaded", function () {

    console.log(
        "Student Collaborations loaded successfully."
    );


    const searchInput =
        document.querySelector(
            ".collaboration-search input"
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


    const cards =
        document.querySelectorAll(
            ".collaboration-card"
        );


    cards.forEach(function (card, index) {

        card.style.opacity = "0";
        card.style.transform = "translateY(8px)";

        setTimeout(function () {

            card.style.transition =
                "opacity .25s ease, transform .25s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, index * 50);

    });

});