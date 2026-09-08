document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
       ===================================================== */

    const messageSearch =
        document.getElementById("messageSearch");

    const messageList =
        document.getElementById("messageList");

    const searchEmpty =
        document.getElementById("messageSearchEmpty");

    const clearSearch =
        document.getElementById("clearMessageSearch");

    const folderTitle =
        document.getElementById("messageFolderTitle");

    const folderSubtitle =
        document.getElementById("messageFolderSubtitle");

    const composeModal =
        document.getElementById("composeModal");

    const viewMessageModal =
        document.getElementById("viewMessageModal");

    const openComposeBtn =
        document.getElementById("openComposeBtn");

    const emptyComposeBtn =
        document.getElementById("emptyComposeBtn");


    /* =====================================================
       FOLDER SWITCHING
       ===================================================== */

    const folders =
        document.querySelectorAll(".message-folder");

    const messages =
        document.querySelectorAll(".message-item");


    const folderData = {

        inbox: {
            title: "Inbox",
            subtitle: "Messages received by your organization."
        },

        sent: {
            title: "Sent",
            subtitle: "Messages sent by your organization."
        },

        unread: {
            title: "Unread",
            subtitle: "Messages that are waiting for your attention."
        }

    };


    function updateMessageFolder(folder) {

        folders.forEach(function (button) {

            button.classList.remove("active");

            if (button.dataset.folder === folder) {
                button.classList.add("active");
            }

        });


        if (folderData[folder]) {

            folderTitle.textContent =
                folderData[folder].title;

            folderSubtitle.textContent =
                folderData[folder].subtitle;

        }


        if (messageSearch) {
            messageSearch.value = "";
        }


        let visibleCount = 0;


        messages.forEach(function (message) {

            const messageFolder =
                message.dataset.folder;

            let shouldShow = false;


            if (folder === "inbox") {

                shouldShow =
                    messageFolder === "inbox";

            } else if (folder === "sent") {

                shouldShow =
                    messageFolder === "sent";

            } else if (folder === "unread") {

                shouldShow =
                    message.classList.contains("unread");

            }


            message.style.display =
                shouldShow ? "flex" : "none";


            if (shouldShow) {
                visibleCount++;
            }

        });


        if (searchEmpty) {

            searchEmpty.style.display =
                visibleCount === 0 && messages.length > 0
                    ? "flex"
                    : "none";

        }

    }


    folders.forEach(function (folderButton) {

        folderButton.addEventListener("click", function () {

            updateMessageFolder(
                folderButton.dataset.folder
            );

        });

    });


    /* =====================================================
       SEARCH
       ===================================================== */

    function searchMessages() {

        if (!messageSearch) {
            return;
        }


        const searchTerm =
            messageSearch.value
                .trim()
                .toLowerCase();


        const activeFolder =
            document.querySelector(
                ".message-folder.active"
            );


        const folder =
            activeFolder
                ? activeFolder.dataset.folder
                : "inbox";


        let visibleCount = 0;


        messages.forEach(function (message) {

            const messageFolder =
                message.dataset.folder;

            const searchableText =
                message.dataset.search || "";


            let folderMatch = false;


            if (folder === "inbox") {

                folderMatch =
                    messageFolder === "inbox";

            } else if (folder === "sent") {

                folderMatch =
                    messageFolder === "sent";

            } else if (folder === "unread") {

                folderMatch =
                    message.classList.contains("unread");

            }


            const searchMatch =
                !searchTerm ||
                searchableText.includes(searchTerm);


            const shouldShow =
                folderMatch && searchMatch;


            message.style.display =
                shouldShow ? "flex" : "none";


            if (shouldShow) {
                visibleCount++;
            }

        });


        if (searchEmpty) {

            searchEmpty.style.display =
                visibleCount === 0 && messages.length > 0
                    ? "flex"
                    : "none";

        }

    }


    if (messageSearch) {

        messageSearch.addEventListener(
            "input",
            searchMessages
        );

    }


    if (clearSearch) {

        clearSearch.addEventListener(
            "click",
            function () {

                messageSearch.value = "";

                searchMessages();

                messageSearch.focus();

            }
        );

    }


    /* =====================================================
       MODAL HELPERS
       ===================================================== */

    function openModal(modal) {

        if (!modal) {
            return;
        }

        modal.style.display = "block";

        document.body.style.overflow = "hidden";

    }


    function closeModal(modal) {

        if (!modal) {
            return;
        }

        modal.style.display = "none";

        document.body.style.overflow = "";

    }


    /* =====================================================
       COMPOSE MESSAGE
       ===================================================== */

    if (openComposeBtn) {

        openComposeBtn.addEventListener(
            "click",
            function () {

                openModal(composeModal);

            }
        );

    }


    if (emptyComposeBtn) {

        emptyComposeBtn.addEventListener(
            "click",
            function () {

                openModal(composeModal);

            }
        );

    }


    /* =====================================================
       CLOSE MODALS
       ===================================================== */

    document
        .querySelectorAll("[data-close-modal]")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const modalId =
                        button.dataset.closeModal;

                    const modal =
                        document.getElementById(modalId);

                    closeModal(modal);

                }
            );

        });


    /* =====================================================
       OVERLAY CLOSE
       ===================================================== */

    document
        .querySelectorAll(".messages-modal-overlay")
        .forEach(function (overlay) {

            overlay.addEventListener(
                "click",
                function () {

                    const modal =
                        overlay.closest(".messages-modal");

                    closeModal(modal);

                }
            );

        });


    /* =====================================================
       ESC KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key !== "Escape") {
                return;
            }


            closeModal(composeModal);

            closeModal(viewMessageModal);

        }
    );


    /* =====================================================
       VIEW MESSAGE
       ===================================================== */

    const viewButtons =
        document.querySelectorAll(
            ".message-open-btn"
        );


    viewButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();


                const messageItem =
                    button.closest(".message-item");


                if (!messageItem) {
                    return;
                }


                const sender =
                    messageItem.querySelector(
                        ".message-person strong"
                    );

                const subject =
                    messageItem.querySelector(
                        ".message-content h3"
                    );

                const body =
                    messageItem.querySelector(
                        ".message-content p"
                    );

                const avatar =
                    messageItem.querySelector(
                        ".message-avatar"
                    );

                const date =
                    messageItem.querySelector(
                        ".message-top-row time"
                    );


                const viewSender =
                    document.getElementById(
                        "viewMessageSender"
                    );

                const viewSubject =
                    document.getElementById(
                        "viewMessageSubject"
                    );

                const viewText =
                    document.getElementById(
                        "viewMessageText"
                    );

                const viewAvatar =
                    document.getElementById(
                        "viewMessageAvatar"
                    );

                const viewDate =
                    document.getElementById(
                        "viewMessageDate"
                    );


                if (viewSender && sender) {
                    viewSender.textContent =
                        sender.textContent.trim();
                }


                if (viewSubject && subject) {
                    viewSubject.textContent =
                        subject.textContent.trim();
                }


                if (viewText && body) {
                    viewText.textContent =
                        body.textContent.trim();
                }


                if (viewAvatar && avatar) {
                    viewAvatar.textContent =
                        avatar.textContent.trim();
                }


                if (viewDate && date) {
                    viewDate.textContent =
                        date.textContent.trim();
                }


                openModal(viewMessageModal);

            }
        );

    });


    /* =====================================================
       CLICK MESSAGE ROW
       ===================================================== */

    messages.forEach(function (message) {

        message.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.closest(
                        ".message-open-btn"
                    )
                ) {
                    return;
                }


                const viewButton =
                    message.querySelector(
                        ".message-open-btn"
                    );


                if (viewButton) {
                    viewButton.click();
                }

            }
        );

    });


    /* =====================================================
       COMPOSE FORM UI
       Backend connection will be added later.
       ===================================================== */

    const composeForm =
        document.getElementById(
            "composeMessageForm"
        );


    if (composeForm) {

        composeForm.addEventListener(
            "submit",
            function () {

                const submitButton =
                    composeForm.querySelector(
                        'button[type="submit"]'
                    );


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.textContent =
                        "Sending...";

                }

            }
        );

    }


    /* =====================================================
       INITIAL STATE
       ===================================================== */

    updateMessageFolder("inbox");

});