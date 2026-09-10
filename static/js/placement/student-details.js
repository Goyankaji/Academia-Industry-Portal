document.addEventListener("DOMContentLoaded", function () {

    const skillBars =
        document.querySelectorAll(".skill-progress-value");

    skillBars.forEach(function (bar) {

        const width =
            bar.dataset.width || 0;

        setTimeout(function () {

            bar.style.width = width + "%";

        }, 150);

    });

});