document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       PROFILE COMPLETION
    ====================================================== */

    const progressBar =
        document.querySelector(".completion-fill");

    if (progressBar) {

        let progress = parseInt(
            progressBar.getAttribute("data-progress") || "0",
            10
        );

        if (isNaN(progress)) {
            progress = 0;
        }

        progress = Math.max(0, Math.min(100, progress));

        setTimeout(function () {
            progressBar.style.width = progress + "%";
        }, 250);
    }


    /* =====================================================
       SECTION ENTRANCE
    ====================================================== */

    const sections =
        document.querySelectorAll(
            ".profile-section, .completion-card, .profile-hero"
        );

    sections.forEach(function (section, index) {

        section.style.opacity = "0";
        section.style.transform = "translateY(8px)";

        setTimeout(function () {

            section.style.transition =
                "opacity 0.4s ease, transform 0.4s ease";

            section.style.opacity = "1";
            section.style.transform = "translateY(0)";

        }, 70 + (index * 50));

    });


    console.log(
        "SIH College Profile View loaded successfully."
    );

});