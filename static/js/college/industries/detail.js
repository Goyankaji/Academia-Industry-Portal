document.addEventListener("DOMContentLoaded", function () {

    const websiteLink = document.querySelector(".website-link");

    if (websiteLink) {
        websiteLink.addEventListener("click", function () {
            console.log("Opening industry website...");
        });
    }

});