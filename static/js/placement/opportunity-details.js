document.addEventListener("DOMContentLoaded", function () {

    // Back button handling
    const backButton = document.querySelector(".back-button");

    if (backButton) {
        backButton.addEventListener("click", function (event) {
            event.preventDefault();
            window.history.back();
        });
    }

    // Copy opportunity ID if copy button exists
    const copyButtons = document.querySelectorAll("[data-copy]");

    copyButtons.forEach(button => {
        button.addEventListener("click", function () {
            const text = this.getAttribute("data-copy");

            if (!text) {
                return;
            }

            navigator.clipboard.writeText(text)
                .then(() => {
                    const originalText = this.innerHTML;

                    this.innerHTML = '<i class="fa-solid fa-check"></i> Copied';

                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 1500);
                })
                .catch(() => {
                    console.warn("Unable to copy text.");
                });
        });
    });

});