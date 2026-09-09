document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PROFILE PROGRESS ANIMATION
    ====================================================== */

    const progressBars = document.querySelectorAll(".progress-fill");

    progressBars.forEach(function (bar) {

        let progress = parseInt(
            bar.getAttribute("data-progress") || "0",
            10
        );

        if (isNaN(progress)) {
            progress = 0;
        }

        progress = Math.max(0, Math.min(100, progress));

        setTimeout(function () {
            bar.style.width = progress + "%";
        }, 250);
    });


    /* =====================================================
       STAT COUNTER ANIMATION
    ====================================================== */

    const counters = document.querySelectorAll("[data-count]");

    counters.forEach(function (counter) {

        const target = parseInt(
            counter.getAttribute("data-count") || "0",
            10
        );

        if (isNaN(target)) {
            return;
        }

        let current = 0;

        const duration = 700;
        const steps = 30;
        const increment = target / steps;
        const intervalTime = duration / steps;

        const timer = setInterval(function () {

            current += increment;

            if (current >= target) {
                current = target;
                clearInterval(timer);
            }

            counter.textContent = Math.floor(current);

        }, intervalTime);
    });


    /* =====================================================
       PANEL ENTRANCE
    ====================================================== */

    const panels = document.querySelectorAll(
        ".dashboard-panel, .stat-card, .dashboard-welcome"
    );

    panels.forEach(function (panel, index) {

        panel.style.opacity = "0";
        panel.style.transform = "translateY(10px)";

        setTimeout(function () {

            panel.style.transition =
                "opacity 0.45s ease, transform 0.45s ease";

            panel.style.opacity = "1";
            panel.style.transform = "translateY(0)";

        }, 80 + (index * 35));
    });


    /* =====================================================
       DEPARTMENT CARD INTERACTION
    ====================================================== */

    const departmentCards =
        document.querySelectorAll(".department-card");

    departmentCards.forEach(function (card) {

        card.addEventListener("click", function () {

            const departmentName =
                card.querySelector("h3");

            if (departmentName) {

                console.log(
                    "Department selected:",
                    departmentName.textContent.trim()
                );
            }

        });

    });


    console.log(
        "SIH College Dashboard loaded successfully."
    );

});