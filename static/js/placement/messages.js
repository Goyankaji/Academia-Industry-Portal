/* =========================================================
   PLACEMENT CELL - MESSAGES
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const composeModal =
        document.getElementById("composeModal");

    const openComposeBtn =
        document.getElementById("openComposeBtn");

    const closeComposeBtn =
        document.getElementById("closeComposeBtn");

    const cancelComposeBtn =
        document.getElementById("cancelComposeBtn");

    const composeForm =
        document.getElementById("composeMessageForm");

    const sendMessageBtn =
        document.getElementById("sendMessageBtn");

    const toast =
        document.getElementById("messageToast");


    /* =====================================================
       OPEN MODAL
    ===================================================== */

    function openModal() {

        if (!composeModal) return;

        composeModal.classList.add("show");

        document.body.style.overflow = "hidden";
    }


    /* =====================================================
       CLOSE MODAL
    ===================================================== */

    function closeModal() {

        if (!composeModal) return;

        composeModal.classList.remove("show");

        document.body.style.overflow = "";

        if (composeForm) {
            composeForm.reset();
        }
    }


    if (openComposeBtn) {
        openComposeBtn.addEventListener(
            "click",
            openModal
        );
    }


    if (closeComposeBtn) {
        closeComposeBtn.addEventListener(
            "click",
            closeModal
        );
    }


    if (cancelComposeBtn) {
        cancelComposeBtn.addEventListener(
            "click",
            closeModal
        );
    }


    /* =====================================================
       CLOSE WHEN CLICKING OUTSIDE
    ===================================================== */

    if (composeModal) {

        composeModal.addEventListener(
            "click",
            (event) => {

                if (
                    event.target === composeModal
                ) {
                    closeModal();
                }

            }
        );
    }


    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                composeModal &&
                composeModal.classList.contains("show")
            ) {
                closeModal();
            }

        }
    );


    /* =====================================================
       TOAST
    ===================================================== */

    function showToast(
        message,
        duration = 3000
    ) {

        if (!toast) return;

        toast.textContent = message;

        toast.classList.add("show");

        setTimeout(() => {

            toast.classList.remove("show");

        }, duration);
    }


    /* =====================================================
       MARK MESSAGE AS READ
    ===================================================== */

    const markReadButtons =
        document.querySelectorAll(
            ".mark-read-btn"
        );


    markReadButtons.forEach(
        (button) => {

            button.addEventListener(
                "click",
                async (event) => {

                    event.stopPropagation();

                    const messageId =
                        button.dataset.messageId;

                    if (!messageId) return;


                    button.disabled = true;

                    button.textContent =
                        "Updating...";


                    try {

                        const response =
                            await fetch(
                                `/placement/messages/${messageId}/read`,
                                {
                                    method: "POST",
                                    headers: {
                                        "X-Requested-With":
                                            "XMLHttpRequest"
                                    }
                                }
                            );


                        const data =
                            await response.json();


                        if (!response.ok || !data.success) {

                            throw new Error(
                                data.message ||
                                "Unable to mark message as read."
                            );

                        }


                        const row =
                            button.closest(
                                ".message-row"
                            );


                        if (row) {

                            row.classList.remove(
                                "unread"
                            );

                            row.dataset.isRead = "1";


                            const status =
                                row.querySelector(
                                    ".read-status"
                                );

                            if (status) {

                                status.className =
                                    "read-status read";

                                status.textContent =
                                    "✓ Read";
                            }


                            button.remove();
                        }


                        showToast(
                            "Message marked as read."
                        );


                    } catch (error) {

                        console.error(
                            "Mark read error:",
                            error
                        );

                        button.disabled = false;

                        button.textContent =
                            "Mark as read";

                        showToast(
                            error.message ||
                            "Unable to update message."
                        );
                    }

                }
            );

        }
    );


    /* =====================================================
       SEND MESSAGE
    ===================================================== */

    if (composeForm) {

        composeForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();


                const receiver =
                    document.getElementById(
                        "receiver_id"
                    );

                const subject =
                    document.getElementById(
                        "subject"
                    );

                const message =
                    document.getElementById(
                        "message"
                    );


                if (
                    !receiver ||
                    !subject ||
                    !message
                ) {
                    return;
                }


                if (!receiver.value) {

                    showToast(
                        "Please select a recipient."
                    );

                    receiver.focus();

                    return;
                }


                if (!subject.value.trim()) {

                    showToast(
                        "Please enter a subject."
                    );

                    subject.focus();

                    return;
                }


                if (!message.value.trim()) {

                    showToast(
                        "Please enter a message."
                    );

                    message.focus();

                    return;
                }


                sendMessageBtn.disabled = true;

                sendMessageBtn.textContent =
                    "Sending...";


                try {

                    const formData =
                        new FormData(
                            composeForm
                        );


                    const response =
                        await fetch(
                            "{{ url_for('placement_send_message') }}",
                            {
                                method: "POST",
                                body: formData,
                                headers: {
                                    "X-Requested-With":
                                        "XMLHttpRequest"
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
                            "Unable to send message."
                        );

                    }


                    closeModal();


                    showToast(
                        "Message sent successfully."
                    );


                    /*
                     * Reload after short delay
                     * so sent message appears in Sent folder.
                     */

                    setTimeout(() => {

                        window.location.href =
                            "{{ url_for('placement_messages', folder='sent') }}";

                    }, 900);


                } catch (error) {

                    console.error(
                        "Send message error:",
                        error
                    );

                    showToast(
                        error.message ||
                        "Unable to send message."
                    );

                } finally {

                    sendMessageBtn.disabled = false;

                    sendMessageBtn.textContent =
                        "Send Message";
                }

            }
        );
    }


    /* =====================================================
       MESSAGE ROW CLICK
    ===================================================== */

    document.querySelectorAll(
        ".message-row"
    ).forEach(
        (row) => {

            row.addEventListener(
                "click",
                (event) => {

                    if (
                        event.target.closest(
                            ".mark-read-btn"
                        )
                    ) {
                        return;
                    }

                    const button =
                        row.querySelector(
                            ".mark-read-btn"
                        );

                    if (button) {
                        button.click();
                    }

                }
            );

        }
    );

});