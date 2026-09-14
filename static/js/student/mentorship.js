/* =========================================================
   STUDENT MENTORSHIP
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("mentorSearch");

    const mentorCards =
        Array.from(
            document.querySelectorAll(".mentor-card")
        );

    const searchEmpty =
        document.getElementById("mentorSearchEmpty");


    function filterMentors() {

        if (!searchInput) {
            return;
        }

        const query =
            searchInput.value
                .trim()
                .toLowerCase();

        let visibleCount = 0;


        mentorCards.forEach(function (card) {

            const name =
                card.dataset.name || "";

            const email =
                card.dataset.email || "";

            const matches =
                name.includes(query) ||
                email.includes(query);


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
            filterMentors
        );

    }


    // -----------------------------------------------------
    // Prevent double submission
    // -----------------------------------------------------

    document
        .querySelectorAll(".mentor-request-form")
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
                        "Sending Request...";

                }
            );

        });

});