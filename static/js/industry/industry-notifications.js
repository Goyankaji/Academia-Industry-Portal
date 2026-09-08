document.addEventListener("DOMContentLoaded", function () {

    const notificationSearch =
        document.getElementById("notificationSearch");

    const notificationCards =
        Array.from(
            document.querySelectorAll(".notification-card")
        );

    const noResults =
        document.getElementById("notificationNoResults");

    const clearFilters =
        document.getElementById("clearNotificationFilters");

    const sideItems =
        document.querySelectorAll(
            ".notifications-side-item"
        );

    const typeItems =
        document.querySelectorAll(
            ".notifications-type-item"
        );

    const sectionTitle =
        document.getElementById(
            "notificationSectionTitle"
        );

    const sectionSubtitle =
        document.getElementById(
            "notificationSectionSubtitle"
        );


    let currentFilter = "all";
    let currentType = "all";


    /* ========================================================
       FILTER NOTIFICATIONS
    ======================================================== */

    function filterNotifications() {

        const searchValue =
            notificationSearch
                ? notificationSearch.value
                    .trim()
                    .toLowerCase()
                : "";

        let visibleCount = 0;


        notificationCards.forEach(function (card) {

            const isRead =
                card.dataset.read === "1";

            const type =
                (card.dataset.type || "SYSTEM")
                    .toUpperCase();

            const searchText =
                (card.dataset.search || "")
                    .toLowerCase();


            /* STATUS FILTER */

            let matchesStatus = true;

            if (currentFilter === "unread") {
                matchesStatus = !isRead;
            }

            if (currentFilter === "read") {
                matchesStatus = isRead;
            }


            /* TYPE FILTER */

            let matchesType = true;

            if (currentType !== "all") {
                matchesType =
                    type === currentType;
            }


            /* SEARCH FILTER */

            const matchesSearch =
                searchText.includes(searchValue);


            /* FINAL RESULT */

            const shouldShow =
                matchesStatus &&
                matchesType &&
                matchesSearch;


            if (shouldShow) {

                card.classList.remove(
                    "notification-hidden"
                );

                visibleCount++;

            } else {

                card.classList.add(
                    "notification-hidden"
                );

            }

        });


        /* ====================================================
           FILTER EMPTY STATE
        ==================================================== */

        if (noResults) {

            /*
             * Agar database mein notifications hi nahi hain,
             * to "No Notifications Found" nahi dikhana.
             * Normal "No Notifications" HTML state hi rahega.
             */

            if (notificationCards.length === 0) {

                noResults.style.display = "none";

            } else {

                noResults.style.display =
                    visibleCount === 0
                        ? "flex"
                        : "none";
            }
        }

    }


    /* ========================================================
       STATUS FILTER
    ======================================================== */

    sideItems.forEach(function (item) {

        item.addEventListener(
            "click",
            function () {

                sideItems.forEach(function (button) {
                    button.classList.remove("active");
                });

                item.classList.add("active");


                currentFilter =
                    item.dataset.filter || "all";


                /* UPDATE TITLE */

                if (sectionTitle) {

                    if (currentFilter === "unread") {

                        sectionTitle.textContent =
                            "Unread Notifications";

                    } else if (
                        currentFilter === "read"
                    ) {

                        sectionTitle.textContent =
                            "Read Notifications";

                    } else {

                        sectionTitle.textContent =
                            "All Notifications";
                    }
                }


                /* UPDATE SUBTITLE */

                if (sectionSubtitle) {

                    if (currentFilter === "unread") {

                        sectionSubtitle.textContent =
                            "Notifications that still need your attention.";

                    } else if (
                        currentFilter === "read"
                    ) {

                        sectionSubtitle.textContent =
                            "Notifications you have already viewed.";

                    } else {

                        sectionSubtitle.textContent =
                            "All notifications received by your organization.";
                    }
                }


                filterNotifications();

            }
        );

    });


    /* ========================================================
       TYPE FILTER
    ======================================================== */

    typeItems.forEach(function (item) {

        item.addEventListener(
            "click",
            function () {

                const selectedType =
                    item.dataset.type || "all";


                if (currentType === selectedType) {

                    currentType = "all";

                    item.classList.remove("active");

                } else {

                    typeItems.forEach(function (button) {
                        button.classList.remove("active");
                    });

                    currentType = selectedType;

                    item.classList.add("active");
                }


                filterNotifications();

            }
        );

    });


    /* ========================================================
       SEARCH
    ======================================================== */

    if (notificationSearch) {

        notificationSearch.addEventListener(
            "input",
            function () {

                filterNotifications();

            }
        );

    }


    /* ========================================================
       CLEAR FILTERS
    ======================================================== */

    if (clearFilters) {

        clearFilters.addEventListener(
            "click",
            function () {

                currentFilter = "all";
                currentType = "all";


                /* RESET SEARCH */

                if (notificationSearch) {
                    notificationSearch.value = "";
                }


                /* RESET STATUS */

                sideItems.forEach(function (button) {

                    button.classList.remove("active");

                    if (
                        button.dataset.filter === "all"
                    ) {
                        button.classList.add("active");
                    }

                });


                /* RESET TYPES */

                typeItems.forEach(function (button) {
                    button.classList.remove("active");
                });


                /* RESET HEADING */

                if (sectionTitle) {

                    sectionTitle.textContent =
                        "All Notifications";

                }


                /* RESET SUBTITLE */

                if (sectionSubtitle) {

                    sectionSubtitle.textContent =
                        "All notifications received by your organization.";

                }


                filterNotifications();

            }
        );

    }


    /* ========================================================
       INITIAL FILTER
    ======================================================== */

    filterNotifications();


    /* ========================================================
       MARK ALL AS READ CONFIRMATION
    ======================================================== */

    const markAllForm =
        document.querySelector(
            ".notifications-header-action form"
        );


    if (markAllForm) {

        markAllForm.addEventListener(
            "submit",
            function (event) {

                const confirmed =
                    window.confirm(
                        "Mark all notifications as read?"
                    );

                if (!confirmed) {S
                    event.preventDefault();
                }

            }
        );

    }

});