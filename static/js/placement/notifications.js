/* ============================================
   PLACEMENT CELL - NOTIFICATIONS
   ============================================ */

document.addEventListener("DOMContentLoaded", function () {

    /* -----------------------------------------
       Confirm Mark All as Read
       ----------------------------------------- */

    const markAllForm = document.getElementById("markAllForm");

    if (markAllForm) {
        markAllForm.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to mark all notifications as read?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });
    }


    /* -----------------------------------------
       Mark Individual Notification as Read
       ----------------------------------------- */

    const markReadForms = document.querySelectorAll(".mark-read-form");

    markReadForms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const button = form.querySelector(".mark-read-btn");

            if (button) {
                button.disabled = true;
                button.innerHTML =
                    '<i class="fas fa-spinner fa-spin"></i> Marking...';
            }

        });

    });


    /* -----------------------------------------
       Relative Notification Time
       ----------------------------------------- */

    const timeElements = document.querySelectorAll(".notification-time[data-time]");

    timeElements.forEach(function (element) {

        const rawTime = element.getAttribute("data-time");

        if (!rawTime) {
            return;
        }

        const date = new Date(rawTime);

        if (isNaN(date.getTime())) {
            return;
        }

        const now = new Date();
        const diff = Math.floor((now - date) / 1000);

        let text;

        if (diff < 60) {
            text = "Just now";
        } else if (diff < 3600) {
            const minutes = Math.floor(diff / 60);
            text = minutes + (minutes === 1 ? " minute ago" : " minutes ago");
        } else if (diff < 86400) {
            const hours = Math.floor(diff / 3600);
            text = hours + (hours === 1 ? " hour ago" : " hours ago");
        } else if (diff < 604800) {
            const days = Math.floor(diff / 86400);
            text = days + (days === 1 ? " day ago" : " days ago");
        } else {
            text = date.toLocaleDateString("en-IN", {
                day: "2-digit",
                month: "short",
                year: "numeric"
            });
        }

        element.textContent = text;

    });


    /* -----------------------------------------
       Notification Item Hover
       ----------------------------------------- */

    const notificationItems =
        document.querySelectorAll(".notification-item");

    notificationItems.forEach(function (item) {

        item.addEventListener("mouseenter", function () {
            item.classList.add("notification-hover");
        });

        item.addEventListener("mouseleave", function () {
            item.classList.remove("notification-hover");
        });

    });

});