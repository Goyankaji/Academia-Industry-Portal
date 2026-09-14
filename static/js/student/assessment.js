document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ASSESSMENT LIST PAGE
    // =====================================================

    const assessmentLinks =
        document.querySelectorAll(
            ".assessment-btn.primary"
        );

    assessmentLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                // Prevent double click
                link.style.pointerEvents = "none";
                link.style.opacity = "0.7";

            }
        );

    });


    // =====================================================
    // ASSESSMENT TAKING PAGE
    // =====================================================

    const assessmentForm =
        document.getElementById(
            "assessmentForm"
        );

    const timerElement =
        document.getElementById(
            "assessmentTimer"
        );


    // If this is not the assessment-taking page,
    // nothing else needs to run.
    if (
        !assessmentForm ||
        !timerElement
    ) {

        return;

    }


    // =====================================================
    // TIMER
    // =====================================================

    let durationMinutes =
        parseInt(
            timerElement.dataset.duration,
            10
        );


    // Default duration
    if (
        isNaN(durationMinutes) ||
        durationMinutes <= 0
    ) {

        durationMinutes = 30;

    }


    let remainingSeconds =
        durationMinutes * 60;


    let timerInterval;


    function updateTimer() {

        const minutes =
            Math.floor(
                remainingSeconds / 60
            );


        const seconds =
            remainingSeconds % 60;


        timerElement.textContent =
            String(minutes).padStart(2, "0")
            + ":"
            + String(seconds).padStart(2, "0");


        // Time finished
        if (
            remainingSeconds <= 0
        ) {

            clearInterval(
                timerInterval
            );


            timerElement.textContent =
                "00:00";


            // Mark as automatic submission
            assessmentForm.dataset.autoSubmit =
                "true";


            assessmentForm.submit();

            return;

        }


        remainingSeconds--;

    }


    // Initial timer display
    updateTimer();


    // Start timer
    timerInterval =
        setInterval(
            updateTimer,
            1000
        );


    // =====================================================
    // QUESTION / ANSWER PROGRESS
    // =====================================================

    const questionInputs =
        assessmentForm.querySelectorAll(
            'input[type="radio"]'
        );


    const answeredCount =
        document.getElementById(
            "answeredCount"
        );


    const progressBar =
        document.getElementById(
            "assessmentProgress"
        );


    const questionCards =
        document.querySelectorAll(
            ".question-card"
        );


    const questionCount =
        questionCards.length;


    function updateAnswerProgress() {

        let answered = 0;


        questionCards.forEach(
            function (card) {

                const selected =
                    card.querySelector(
                        'input[type="radio"]:checked'
                    );


                if (selected) {

                    answered++;

                }

            }
        );


        // Update answered count
        if (answeredCount) {

            answeredCount.textContent =
                answered
                + " / "
                + questionCount;

        }


        // Update progress bar
        if (progressBar) {

            const percentage =
                questionCount > 0
                    ? (
                        answered /
                        questionCount
                    ) * 100
                    : 0;


            progressBar.style.width =
                percentage + "%";

        }

    }


    // Listen for answer selection
    questionInputs.forEach(
        function (input) {

            input.addEventListener(
                "change",
                updateAnswerProgress
            );

        }
    );


    // Initial progress
    updateAnswerProgress();


    // =====================================================
    // SUBMIT CONFIRMATION
    // =====================================================

    assessmentForm.addEventListener(
        "submit",
        function (event) {


            // If timer automatically submitted,
            // don't show confirmation.
            if (
                assessmentForm.dataset.autoSubmit
                === "true"
            ) {

                return;

            }


            const totalQuestions =
                document.querySelectorAll(
                    ".question-card"
                ).length;


            const answeredQuestions =
                document.querySelectorAll(
                    ".question-card input[type='radio']:checked"
                ).length;


            const unanswered =
                totalQuestions -
                answeredQuestions;


            // -------------------------------------------------
            // Unanswered questions
            // -------------------------------------------------

            if (
                unanswered > 0
            ) {

                const confirmed =
                    window.confirm(
                        "You have "
                        + unanswered
                        + " unanswered question(s). "
                        + "Unanswered questions will be treated as incorrect. "
                        + "Submit anyway?"
                    );


                if (!confirmed) {

                    event.preventDefault();

                    return;

                }

            }


            // -------------------------------------------------
            // Disable submit button
            // -------------------------------------------------

            const submitButton =
                document.getElementById(
                    "submitAssessment"
                );


            if (submitButton) {

                submitButton.disabled =
                    true;


                submitButton.textContent =
                    "Submitting...";

            }

        }
    );


    // =====================================================
    // PREVENT ACCIDENTAL PAGE LEAVE
    // =====================================================

    let hasSubmitted = false;


    assessmentForm.addEventListener(
        "submit",
        function () {

            hasSubmitted = true;

        }
    );


    window.addEventListener(
        "beforeunload",
        function (event) {

            if (
                !hasSubmitted &&
                remainingSeconds > 0
            ) {

                event.preventDefault();

                event.returnValue = "";

            }

        }
    );


    // =====================================================
    // QUESTION NAVIGATION
    // =====================================================

    const questionButtons =
        document.querySelectorAll(
            "[data-question-index]"
        );


    questionButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const index =
                        this.dataset.questionIndex;


                    const target =
                        document.querySelector(
                            '[data-question="' +
                            index +
                            '"]'
                        );


                    if (target) {

                        target.scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });

                    }

                }
            );

        }
    );


});