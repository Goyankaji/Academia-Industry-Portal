document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("departmentForm");
    const nameInput = document.getElementById("department_name");
    const codeInput = document.getElementById("department_code");
    const descriptionInput = document.getElementById("description");
    const statusInput = document.getElementById("status");

    const previewName = document.getElementById("previewName");
    const previewCode = document.getElementById("previewCode");
    const previewDescription = document.getElementById("previewDescription");
    const descriptionCount = document.getElementById("descriptionCount");

    function updatePreview() {
        previewName.textContent =
            nameInput.value.trim() || "Department Name";

        previewCode.textContent =
            codeInput.value.trim().toUpperCase() || "CODE";

        previewDescription.textContent =
            descriptionInput.value.trim() ||
            "Department description will appear here.";
    }

    nameInput.addEventListener("input", updatePreview);

    codeInput.addEventListener("input", function () {
        this.value = this.value.toUpperCase();
        updatePreview();
    });

    descriptionInput.addEventListener("input", function () {
        descriptionCount.textContent = this.value.length;
        updatePreview();
    });

    statusInput.addEventListener("change", function () {
        const status = document.querySelector(".preview-status");

        if (this.value === "ACTIVE") {
            status.innerHTML = '<span></span> Active';
            status.style.color = "#15803d";
            status.style.background = "#f0fdf4";
        } else {
            status.innerHTML = '<span></span> Inactive';
            status.style.color = "#64748b";
            status.style.background = "#f1f5f9";
            status.querySelector("span").style.background = "#94a3b8";
        }
    });

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

        const saveBtn = document.getElementById("saveBtn");
        saveBtn.disabled = true;
        saveBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';
    });

});