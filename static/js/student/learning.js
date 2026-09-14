document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================================
        // LEARNING PROGRAM CARDS
        // =====================================================

        const programCards =
            document.querySelectorAll(
                ".learning-program-card"
            );


        programCards.forEach(
            function (card, index) {

                card.style.animationDelay =
                    (index * 0.05) + "s";

            }
        );


        // =====================================================
        // EXTERNAL LEARNING LINKS
        // =====================================================

        const learningButtons =
            document.querySelectorAll(
                ".learning-btn:not(.disabled)"
            );


        learningButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        button.classList.add(
                            "learning-opened"
                        );

                    }
                );

            }
        );


    }
);