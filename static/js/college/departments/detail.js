document.addEventListener("DOMContentLoaded", function () {

    const deleteForm = document.getElementById("deleteDepartmentForm");

    if (deleteForm) {

        deleteForm.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this department?\n\n" +
                "This action cannot be undone."
            );

            if (!confirmed) {
                event.preventDefault();
                return;
            }

            const deleteButton =
                deleteForm.querySelector("button[type='submit']");

            deleteButton.disabled = true;

            deleteButton.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...';
        });

    }

});