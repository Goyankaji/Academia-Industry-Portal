/* =========================================================
   STUDENT LIVE PROJECTS
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("liveProjectSearch");

    const cards =
        Array.from(
            document.querySelectorAll(".live-project-card")
        );

    const searchEmpty =
        document.getElementById(
            "liveProjectSearchEmpty"
        );


    function filterProjects() {

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

            const tech =
                card.dataset.tech || "";

            const matches =
                title.includes(query) ||
                tech.includes(query);


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
            filterProjects
        );

    }


    // -----------------------------------------------------
    // Prevent double submission
    // -----------------------------------------------------

    document
        .querySelectorAll(".live-project-card form")
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