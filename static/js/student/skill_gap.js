document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================================
        // GAP SCORE PROGRESS BARS
        // =====================================================

        const gapBars =
            document.querySelectorAll(
                ".gap-score-bar"
            );


        gapBars.forEach(
            function (bar) {

                let score =
                    parseFloat(
                        bar.dataset.score
                    );


                if (isNaN(score)) {

                    score = 0;

                }


                score =
                    Math.max(
                        0,
                        Math.min(
                            100,
                            score
                        )
                    );


                bar.style.width =
                    score + "%";

            }
        );


        // =====================================================
        // GAP CARD ANIMATION
        // =====================================================

        const cards =
            document.querySelectorAll(
                ".skill-gap-card"
            );


        cards.forEach(
            function (card, index) {

                card.style.animationDelay =
                    (index * 0.05) + "s";

            }
        );


        // =====================================================
        // PRIORITY HOVER ACCESSIBILITY
        // =====================================================

        cards.forEach(
            function (card) {

                card.addEventListener(
                    "mouseenter",
                    function () {

                        this.classList.add(
                            "gap-card-hover"
                        );

                    }
                );


                card.addEventListener(
                    "mouseleave",
                    function () {

                        this.classList.remove(
                            "gap-card-hover"
                        );

                    }
                );

            }
        );

    }
);