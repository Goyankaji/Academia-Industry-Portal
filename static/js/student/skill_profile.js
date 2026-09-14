document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================================
        // SKILL SCORE PROGRESS BARS
        // =====================================================

        const scoreBars =
            document.querySelectorAll(
                ".skill-score-bar"
            );


        scoreBars.forEach(
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
        // PROFICIENCY CARD ANIMATION
        // =====================================================

        const cards =
            document.querySelectorAll(
                ".skill-profile-card"
            );


        cards.forEach(
            function (card, index) {

                card.style.animationDelay =
                    (index * 0.05) + "s";

            }
        );


    }
);