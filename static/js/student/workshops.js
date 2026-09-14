/* =========================================================
   STUDENT WORKSHOPS
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("workshopSearch");
    const clearButton = document.getElementById("clearWorkshopSearch");

    const cards = Array.from(
        document.querySelectorAll(".workshop-card")
    );

    const searchEmpty = document.getElementById(
        "workshopSearchEmpty"
    );


    function filterWorkshops() {

        if (!searchInput) {
            return;
        }

        const query = searchInput.value
            .trim()
            .toLowerCase();

        let visibleCount = 0;

        cards.forEach(function (card) {

            const title = card.dataset.title || "";
            const topic = card.dataset.topic || "";

            const matches =
                title.includes(query) ||
                topic.includes(query);

            if (matches) {
                card.style.display = "";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });


        if (searchEmpty) {
            searchEmpty.style.display =
                visibleCount === 0 && query !== ""
                    ? "block"
                    : "none";
        }
    }


    if (searchInput) {
        searchInput.addEventListener(
            "input",
            filterWorkshops
        );
    }


    if (clearButton) {
        clearButton.addEventListener(
            "click",
            function () {

                if (searchInput) {
                    searchInput.value = "";
                    filterWorkshops();
                    searchInput.focus();
                }

            }
        );
    }


    // -----------------------------------------------------
    // Prevent accidental double submit
    // -----------------------------------------------------

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            const button = form.querySelector(
                "button[type='submit']"
            );

            if (!button) {
                return;
            }

            button.disabled = true;

            const originalText = button.innerHTML;

            button.innerHTML = "Processing...";

            setTimeout(function () {

                button.disabled = false;
                button.innerHTML = originalText;

            }, 4000);

        });

    });

});