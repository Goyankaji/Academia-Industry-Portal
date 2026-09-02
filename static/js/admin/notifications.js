document.addEventListener("DOMContentLoaded", function () {

    console.log("SIH Admin Notifications JS loaded successfully.");


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const notificationList =
        document.getElementById("notificationList");

    const searchInput =
        document.getElementById("notificationSearch");

    const filterButtons =
        document.querySelectorAll(".filter-button");

    const refreshButton =
        document.getElementById("refreshNotifications");

    const markAllButton =
        document.getElementById("markAllRead");

    const emptyState =
        document.getElementById("notificationEmpty");

    const visibleCount =
        document.getElementById("visibleCount");


    let activeFilter = "all";


    /* =====================================================
       GET NOTIFICATIONS
       ===================================================== */

    function getNotifications() {

        if (!notificationList) {
            return [];
        }

        return Array.from(
            notificationList.querySelectorAll(
                ".notification-item"
            )
        );

    }


    /* =====================================================
       UPDATE SUMMARY
       ===================================================== */

    function updateSummary() {

        const notifications =
            getNotifications();

        let unread = 0;
        let important = 0;
        let system = 0;


        notifications.forEach(function (item) {

            if (
                item.dataset.read === "false"
            ) {
                unread++;
            }


            if (
                item.dataset.type === "important"
            ) {
                important++;
            }


            if (
                item.dataset.category === "system"
            ) {
                system++;
            }

        });


        const allCount =
            document.getElementById("allCount");

        const unreadCount =
            document.getElementById("unreadCount");

        const importantCount =
            document.getElementById("importantCount");

        const systemCount =
            document.getElementById("systemCount");


        if (allCount) {
            allCount.textContent =
                notifications.length;
        }

        if (unreadCount) {
            unreadCount.textContent =
                unread;
        }

        if (importantCount) {
            importantCount.textContent =
                important;
        }

        if (systemCount) {
            systemCount.textContent =
                system;
        }

    }


    /* =====================================================
       FILTER + SEARCH
       ===================================================== */

    function applyFilters() {

        const notifications =
            getNotifications();

        const searchValue =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";

        let visible = 0;


        notifications.forEach(function (item) {

            const category =
                item.dataset.category || "";

            const type =
                item.dataset.type || "";

            const read =
                item.dataset.read || "true";

            const text =
                item.textContent.toLowerCase();


            let filterMatch = true;


            /* FILTER */

            if (activeFilter === "unread") {

                filterMatch =
                    read === "false";

            }

            else if (activeFilter === "important") {

                filterMatch =
                    type === "important";

            }

            else if (activeFilter === "system") {

                filterMatch =
                    category === "system";

            }

            else if (
                activeFilter === "registration" ||
                activeFilter === "collaboration" ||
                activeFilter === "opportunity"
            ) {

                filterMatch =
                    category === activeFilter;

            }


            /* SEARCH */

            const searchMatch =
                !searchValue ||
                text.includes(searchValue);


            const shouldShow =
                filterMatch && searchMatch;


            item.style.display =
                shouldShow ? "grid" : "none";


            if (shouldShow) {
                visible++;
            }

        });


        if (visibleCount) {
            visibleCount.textContent =
                visible;
        }


        if (emptyState) {

            emptyState.style.display =
                visible === 0
                    ? "block"
                    : "none";

        }

    }


    /* =====================================================
       FILTER BUTTONS
       ===================================================== */

    filterButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                filterButtons.forEach(
                    function (item) {
                        item.classList.remove("active");
                    }
                );


                this.classList.add("active");


                activeFilter =
                    this.dataset.filter || "all";


                applyFilters();

            }
        );

    });


    /* =====================================================
       SEARCH
       ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                applyFilters();

            }
        );

    }


    /* =====================================================
       OPEN RELATED PAGE
       ===================================================== */

    function setupNotificationLinks() {

        const notifications =
            getNotifications();


        notifications.forEach(function (item) {

            item.addEventListener(
                "click",
                function (event) {

                    /*
                     * Do not redirect when clicking
                     * read/delete action buttons.
                     */

                    if (
                        event.target.closest(".read-button") ||
                        event.target.closest(".delete-button")
                    ) {
                        return;
                    }


                    const url =
                        item.dataset.url;


                    if (url) {

                        window.location.href =
                            url;

                    }

                }
            );

        });

    }


    /* =====================================================
       MARK SINGLE AS READ / UNREAD
       ===================================================== */

    function setupNotificationActions() {

        const notifications =
            getNotifications();


        notifications.forEach(function (item) {

            const readButton =
                item.querySelector(".read-button");

            const deleteButton =
                item.querySelector(".delete-button");


            /* =================================================
               MARK READ / UNREAD
               ================================================= */

            if (readButton) {

                readButton.addEventListener(
                    "click",
                    function (event) {

                        event.stopPropagation();


                        const currentlyRead =
                            item.dataset.read === "true";


                        if (currentlyRead) {

                            item.dataset.read =
                                "false";

                            item.classList.add(
                                "unread"
                            );


                            readButton.textContent =
                                "✓";

                            readButton.title =
                                "Mark as read";


                            if (
                                !item.querySelector(
                                    ".unread-dot"
                                )
                            ) {

                                const top =
                                    item.querySelector(
                                        ".notification-top"
                                    );


                                if (top) {

                                    const dot =
                                        document.createElement(
                                            "span"
                                        );

                                    dot.className =
                                        "unread-dot";

                                    top.appendChild(dot);

                                }

                            }

                        }

                        else {

                            item.dataset.read =
                                "true";


                            item.classList.remove(
                                "unread"
                            );


                            readButton.textContent =
                                "↶";

                            readButton.title =
                                "Mark as unread";


                            const dot =
                                item.querySelector(
                                    ".unread-dot"
                                );


                            if (dot) {
                                dot.remove();
                            }

                        }


                        updateSummary();

                        applyFilters();

                    }
                );

            }


            /* =================================================
               DELETE
               ================================================= */

            if (deleteButton) {

                deleteButton.addEventListener(
                    "click",
                    function (event) {

                        event.stopPropagation();


                        item.style.opacity =
                            "0";

                        item.style.transform =
                            "translateX(12px)";


                        setTimeout(
                            function () {

                                item.remove();

                                updateSummary();

                                applyFilters();

                            },
                            180
                        );

                    }
                );

            }

        });

    }


    /* =====================================================
       MARK ALL AS READ
       ===================================================== */

    if (markAllButton) {

        markAllButton.addEventListener(
            "click",
            function () {

                const notifications =
                    getNotifications();


                notifications.forEach(
                    function (item) {

                        item.dataset.read =
                            "true";


                        item.classList.remove(
                            "unread"
                        );


                        const dot =
                            item.querySelector(
                                ".unread-dot"
                            );


                        if (dot) {
                            dot.remove();
                        }


                        const readButton =
                            item.querySelector(
                                ".read-button"
                            );


                        if (readButton) {

                            readButton.textContent =
                                "↶";

                            readButton.title =
                                "Mark as unread";

                        }

                    }
                );


                updateSummary();

                applyFilters();


                markAllButton.innerHTML =
                    "<span>✓</span> All read";


                markAllButton.disabled =
                    true;


                setTimeout(
                    function () {

                        markAllButton.innerHTML =
                            "<span>✓</span> Mark all as read";

                        markAllButton.disabled =
                            false;

                    },
                    1200
                );

            }
        );

    }


    /* =====================================================
       REFRESH
       ===================================================== */

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            function () {

                if (
                    refreshButton.dataset.loading ===
                    "true"
                ) {
                    return;
                }


                refreshButton.dataset.loading =
                    "true";


                refreshButton.innerHTML =
                    "<span>↻</span> Refreshing...";


                setTimeout(
                    function () {

                        window.location.reload();

                    },
                    500
                );

            }
        );

    }


    /* =====================================================
       INITIALIZE
       ===================================================== */

    setupNotificationLinks();

    setupNotificationActions();

    updateSummary();

    applyFilters();

});