document.addEventListener("DOMContentLoaded", function () {

    const deleteForm = document.getElementById("deleteProjectForm");

    if (!deleteForm) {
        return;
    }

    deleteForm.addEventListener("submit", function (event) {

        const confirmed = confirm(
            "Are you sure you want to delete this project?\n\n" +
            "This action cannot be undone."
        );

        if (!confirmed) {
            event.preventDefault();
        }

    });

});