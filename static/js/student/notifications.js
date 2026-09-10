/* =========================================================
   STUDENT NOTIFICATIONS
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const filterForm = document.getElementById(
        "notificationFilterForm"
    );

    const searchInput = document.getElementById(
        "notificationSearch"
    );

    const clearSearchBtn = document.getElementById(
        "clearSearchBtn"
    );

    const typeFilter = document.getElementById(
        "notificationType"
    );

    const markAllReadBtn = document.getElementById(
        "markAllReadBtn"
    );

    const notificationToast = document.getElementById(
        "notificationToast"
    );

    const toastMessage = document.getElementById(
        "toastMessage"
    );


    /* =====================================================
       FORMAT DATES
    ====================================================== */

    function formatDate(dateValue) {

        if (!dateValue) {
            return "—";
        }

        const date = new Date(dateValue);

        if (Number.isNaN(date.getTime())) {
            return dateValue;
        }

        return date.toLocaleString("en-IN", {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    }


    document
        .querySelectorAll(".formatted-date")
        .forEach(function (element) {

            const dateValue = element.dataset.date;

            element.textContent = formatDate(dateValue);

        });


    document
        .querySelectorAll(".notification-time")
        .forEach(function (element) {

            const dateValue = element.dataset.date;

            element.textContent = formatRelativeDate(
                dateValue
            );

            element.title = formatDate(dateValue);

        });


    /* =====================================================
       RELATIVE DATE
    ====================================================== */

    function formatRelativeDate(dateValue) {

        if (!dateValue) {
            return "—";
        }

        const date = new Date(dateValue);

        if (Number.isNaN(date.getTime())) {
            return dateValue;
        }

        const now = new Date();

        const diff = now.getTime() - date.getTime();

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) {
            return "Just now";
        }

        if (minutes < 60) {
            return minutes + (
                minutes === 1 ? " minute ago" : " minutes ago"
            );
        }

        if (hours < 24) {
            return hours + (
                hours === 1 ? " hour ago" : " hours ago"
            );
        }

        if (days < 7) {
            return days + (
                days === 1 ? " day ago" : " days ago"
            );
        }

        return formatDate(dateValue);
    }


    /* =====================================================
       TOAST
    ====================================================== */

    let toastTimer = null;

    function showToast(message) {

        if (!notificationToast) {
            return;
        }

        if (toastMessage) {
            toastMessage.textContent = message;
        }

        notificationToast.classList.add("show");

        clearTimeout(toastTimer);

        toastTimer = setTimeout(function () {

            notificationToast.classList.remove("show");

        }, 2500);
    }


    /* =====================================================
       MARK SINGLE NOTIFICATION AS READ
    ====================================================== */

    async function markNotificationAsRead(
        notificationId,
        button
    ) {

        if (!notificationId) {
            return;
        }

        if (button) {
            button.disabled = true;
            button.textContent = "Updating...";
        }

        try {

            const response = await fetch(
                `/student/notifications/${encodeURIComponent(notificationId)}/read`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.message || "Unable to update notification."
                );
            }


            const card = document.querySelector(
                `.notification-card[data-notification-id="${CSS.escape(notificationId)}"]`
            );


            if (card) {

                card.classList.remove("unread");
                card.classList.add("read");


                const unreadDot = card.querySelector(
                    ".unread-dot"
                );

                if (unreadDot) {
                    unreadDot.remove();
                }


                if (button) {

                    const readLabel = document.createElement(
                        "span"
                    );

                    readLabel.className = "read-label";
                    readLabel.textContent = "✓ Read";

                    button.replaceWith(readLabel);
                }

            }


            showToast(
                data.message || "Notification marked as read."
            );


            updateUnreadCount();

        } catch (error) {

            console.error(
                "Notification update error:",
                error
            );

            if (button) {
                button.disabled = false;
                button.innerHTML = "<span>✓</span> Mark as Read";
            }

            showToast(
                "Unable to update notification."
            );

        }

    }


    /* =====================================================
       SINGLE MARK READ BUTTONS
    ====================================================== */

    document
        .querySelectorAll(".mark-read-btn")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const notificationId =
                        button.dataset.notificationId;

                    markNotificationAsRead(
                        notificationId,
                        button
                    );

                }
            );

        });


    /* =====================================================
       MARK ALL AS READ
    ====================================================== */

    if (markAllReadBtn) {

        markAllReadBtn.addEventListener(
            "click",
            async function () {

                markAllReadBtn.disabled = true;
                markAllReadBtn.textContent =
                    "Updating...";

                try {

                    const response = await fetch(
                        "/student/notifications/mark-all-read",
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            }
                        }
                    );

                    const data =
                        await response.json();

                    if (
                        !response.ok ||
                        !data.success
                    ) {
                        throw new Error(
                            data.message ||
                            "Unable to update notifications."
                        );
                    }


                    document
                        .querySelectorAll(
                            ".notification-card.unread"
                        )
                        .forEach(function (card) {

                            card.classList.remove(
                                "unread"
                            );

                            card.classList.add(
                                "read"
                            );


                            const unreadDot =
                                card.querySelector(
                                    ".unread-dot"
                                );

                            if (unreadDot) {
                                unreadDot.remove();
                            }


                            const markReadButton =
                                card.querySelector(
                                    ".mark-read-btn"
                                );

                            if (markReadButton) {

                                const readLabel =
                                    document.createElement(
                                        "span"
                                    );

                                readLabel.className =
                                    "read-label";

                                readLabel.textContent =
                                    "✓ Read";

                                markReadButton.replaceWith(
                                    readLabel
                                );
                            }

                        });


                    showToast(
                        data.message ||
                        "All notifications marked as read."
                    );


                    updateUnreadCount();


                    setTimeout(function () {

                        window.location.reload();

                    }, 900);

                } catch (error) {

                    console.error(
                        "Mark all notifications error:",
                        error
                    );

                    showToast(
                        "Unable to update notifications."
                    );

                    markAllReadBtn.disabled = false;

                    markAllReadBtn.innerHTML =
                        "<span>✓</span> Mark All as Read";
                }

            }
        );
    }


    /* =====================================================
       UPDATE UNREAD COUNT IN PAGE
    ====================================================== */

    function updateUnreadCount() {

        const unreadCards =
            document.querySelectorAll(
                ".notification-card.unread"
            );

        const unreadCount =
            unreadCards.length;


        const statCards =
            document.querySelectorAll(
                ".stat-card"
            );


        /*
         * Second stat card is the unread card
         */
        if (statCards.length >= 2) {

            const unreadStrong =
                statCards[1].querySelector("strong");

            if (unreadStrong) {
                unreadStrong.textContent =
                    unreadCount;
            }

        }


        /*
         * Hide Mark All button when nothing is unread
         */
        if (
            unreadCount === 0 &&
            markAllReadBtn
        ) {

            markAllReadBtn.style.display =
                "none";
        }

    }


    /* =====================================================
       SEARCH
    ====================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    if (filterForm) {
                        filterForm.submit();
                    }

                }

            }
        );

    }


    /* =====================================================
       TYPE FILTER
    ====================================================== */

    if (typeFilter) {

        typeFilter.addEventListener(
            "change",
            function () {

                if (filterForm) {
                    filterForm.submit();
                }

            }
        );

    }


    /* =====================================================
       CLEAR SEARCH
    ====================================================== */

    if (clearSearchBtn) {

        clearSearchBtn.addEventListener(
            "click",
            function () {

                if (searchInput) {
                    searchInput.value = "";
                }

                if (filterForm) {
                    filterForm.submit();
                }

            }
        );

    }


    /* =====================================================
       CARD ENTRY ANIMATION
    ====================================================== */

    const cards =
        document.querySelectorAll(
            ".notification-card"
        );

    cards.forEach(function (card, index) {

        card.style.opacity = "0";
        card.style.transform = "translateY(8px)";

        setTimeout(function () {

            card.style.transition =
                "opacity 0.25s ease, transform 0.25s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, index * 40);

    });

});