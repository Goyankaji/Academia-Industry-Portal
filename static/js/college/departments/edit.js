document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("departmentEditForm");
    const nameInput = document.getElementById("department_name");
    const codeInput = document.getElementById("department_code");
    const descriptionInput = document.getElementById("description");

    const descriptionCount = document.getElementById("descriptionCount");

    function updateDescriptionCount() {
        descriptionCount.textContent = descriptionInput.value.length;
    }

    codeInput.addEventListener("input", function () {
        this.value = this.value.toUpperCase();
    });

    descriptionInput.addEventListener("input", updateDescriptionCount);

    form.addEventListener("submit", function (event) {

        let valid = true;

        const name = nameInput.value.trim();
        const code = codeInput.value.trim();

        document.getElementById("nameError").textContent = "";
        document.getElementById("codeError").textContent = "";

        if (!name) {
            document.getElementById("nameError").textContent =
                "Department name is required.";
            valid = false;
        }

        if (!code) {
            document.getElementById("codeError").textContent =
                "Department code is required.";
            valid = false;
        } else if (!/^[A-Z0-9_-]+$/i.test(code)) {
            document.getElementById("codeError").textContent =
                "Only letters, numbers, hyphen and underscore are allowed.";
            valid = false;
        }

        if (!valid) {
            event.preventDefault();
            return;
        }

        const updateBtn = document.getElementById("updateBtn");

        updateBtn.disabled = true;
        updateBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
    });

    updateDescriptionCount();

});