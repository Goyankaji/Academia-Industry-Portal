document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.querySelector(
            '.search-box input[name="search"]'
        );

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    this.form.submit();

                }

            }
        );

    }

});