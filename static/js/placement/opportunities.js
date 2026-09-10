document.addEventListener("DOMContentLoaded", function () {

    const search =
        document.querySelector(
            '.opportunity-search input'
        );

    if (search) {

        search.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {
                    this.form.submit();
                }

            }
        );

    }

});