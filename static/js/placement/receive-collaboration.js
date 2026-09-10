document.addEventListener("DOMContentLoaded", function () {

    const page = document.querySelector(".receive-collaboration-page");

    if (!page) return;


    /* =========================================================
       AUTO SUBMIT FILTERS
       ========================================================= */

    const filterForm = page.querySelector(".filters-form");

    if (filterForm) {

        const selects = filterForm.querySelectorAll("select");

        selects.forEach(function (select) {

            select.addEventListener("change", function () {
                filterForm.submit();
            });

        });
    }


    /* =========================================================
       SEARCH - ENTER KEY
       ========================================================= */

    const searchInput = page.querySelector(
        '.search-wrapper input[name="search"]'
    );

    if (searchInput && filterForm) {

        searchInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {
                event.preventDefault();
                filterForm.submit();
            }

        });
    }


    /* =========================================================
       CARD HOVER ACCESSIBILITY
       ========================================================= */

    const cards = page.querySelectorAll(".collaboration-card");

    cards.forEach(function (card) {

        card.addEventListener("mouseenter", function () {
            card.classList.add("is-hovered");
        });

        card.addEventListener("mouseleave", function () {
            card.classList.remove("is-hovered");
        });

    });


    /* =========================================================
       DESCRIPTION TRUNCATION
       ========================================================= */

    const descriptions = page.querySelectorAll(
        ".description-section p"
    );

    descriptions.forEach(function (description) {

        const maxLength = 450;
        const fullText = description.textContent.trim();

        if (fullText.length <= maxLength) {
            return;
        }

        const shortText = fullText.substring(0, maxLength).trim();

        description.textContent = shortText + "...";

    });


    /* =========================================================
       CLEAR SEARCH WITH ESC
       ========================================================= */

    if (searchInput) {

        searchInput.addEventListener("keydown", function (event) {

            if (event.key === "Escape" && searchInput.value) {
                searchInput.value = "";
            }

        });

    }

});