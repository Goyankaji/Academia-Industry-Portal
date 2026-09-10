/* ============================================
   PLACEMENT CELL - PROFILE
   ============================================ */

document.addEventListener("DOMContentLoaded", function () {

    const editBtn =
        document.getElementById("editProfileBtn");

    const modal =
        document.getElementById("profileModal");

    const overlay =
        document.getElementById("modalOverlay");

    const closeBtn =
        document.getElementById("closeProfileModal");

    const cancelBtn =
        document.getElementById("cancelProfileEdit");

    const form =
        document.getElementById("profileForm");


    /* -----------------------------------------
       OPEN MODAL
       ----------------------------------------- */

    function openModal() {

        if (!modal) {
            return;
        }

        modal.classList.add("show");
        document.body.style.overflow = "hidden";

    }


    /* -----------------------------------------
       CLOSE MODAL
       ----------------------------------------- */

    function closeModal() {

        if (!modal) {
            return;
        }

        modal.classList.remove("show");
        document.body.style.overflow = "";

    }


    /* -----------------------------------------
       EVENTS
       ----------------------------------------- */

    if (editBtn) {
        editBtn.addEventListener("click", openModal);
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", closeModal);
    }

    if (overlay) {
        overlay.addEventListener("click", closeModal);
    }


    /* -----------------------------------------
       ESCAPE KEY
       ----------------------------------------- */

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            closeModal();
        }

    });


    /* -----------------------------------------
       FORM SUBMIT
       ----------------------------------------- */

    if (form) {

        form.addEventListener("submit", function () {

            const saveBtn =
                form.querySelector(".save-profile-btn");

            if (saveBtn) {

                saveBtn.disabled = true;

                saveBtn.innerHTML =
                    '<i class="fas fa-spinner fa-spin"></i> Saving...';

            }

        });

    }

});