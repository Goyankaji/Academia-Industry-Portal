/* =========================================================
   STUDENT INNOVATION CHALLENGES
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("challengeSearch");

    const cards =
        Array.from(
            document.querySelectorAll(".innovation-card")
        );

    const searchEmpty =
        document.getElementById(
            "challengeSearchEmpty"
        );


    function filterChallenges() {

        if (!searchInput) {
            return;
        }

        const query =
            searchInput.value
                .trim()
                .toLowerCase();

        let visibleCount = 0;


        cards.forEach(function (card) {

            const title =
                card.dataset.title || "";

            const description =
                card.dataset.description || "";

            const matches =
                title.includes(query) ||
                description.includes(query);


            if (matches) {

                card.style.display = "";
                visibleCount++;

            } else {

                card.style.display = "none";

            }

        });


        if (searchEmpty) {

            searchEmpty.style.display =
                query !== "" && visibleCount === 0
                    ? "block"
                    : "none";

        }

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterChallenges
        );

    }


    // -----------------------------------------------------
    // Prevent double submission
    // -----------------------------------------------------

    document
        .querySelectorAll(
            ".challenge-register-form, .challenge-submit-form"
        )
        .forEach(function (form) {

            form.addEventListener(
                "submit",
                function () {

                    const button =
                        form.querySelector(
                            "button[type='submit']"
                        );

                    if (!button) {
                        return;
                    }

                    button.disabled = true;

                    button.innerHTML =
                        "Processing...";

                }
            );

        });

});