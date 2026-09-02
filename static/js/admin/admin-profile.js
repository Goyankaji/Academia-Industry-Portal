document.addEventListener("DOMContentLoaded", function () {

    console.log("SIH Admin Profile JS loaded.");


    /* =====================================================
       COVER IMAGE PREVIEW
       ===================================================== */

    const coverInput =
        document.getElementById("coverInput");

    const coverPreview =
        document.getElementById("coverPreview");


    if (coverInput) {

        coverInput.addEventListener("change", function () {

            const file = this.files[0];

            if (!file) {
                return;
            }


            if (!file.type.startsWith("image/")) {

                alert("Please select a valid image.");

                this.value = "";

                return;
            }


            const reader =
                new FileReader();


            reader.onload = function (event) {

                coverPreview.src =
                    event.target.result;

                coverPreview.classList.add(
                    "visible"
                );

            };


            reader.readAsDataURL(file);

        });

    }


    /* =====================================================
       PROFILE IMAGE PREVIEW
       ===================================================== */

    const avatarInput =
        document.getElementById("avatarInput");

    const avatarPreview =
        document.getElementById("avatarPreview");


    if (avatarInput) {

        avatarInput.addEventListener(
            "change",
            function () {

                const file = this.files[0];

                if (!file) {
                    return;
                }


                if (!file.type.startsWith("image/")) {

                    alert("Please select a valid image.");

                    this.value = "";

                    return;
                }


                const reader =
                    new FileReader();


                reader.onload = function (event) {

                    avatarPreview.innerHTML = "";

                    const image =
                        document.createElement("img");

                    image.src =
                        event.target.result;

                    image.alt =
                        "Admin Profile Image";

                    avatarPreview.appendChild(image);

                };


                reader.readAsDataURL(file);

            }
        );

    }


    /*  =====================================================
        SAVE IMAGES
        ===================================================== */

        const saveImages =
            document.getElementById("saveImages");


        if (saveImages) {

            saveImages.addEventListener(
                "click",
                async function () {

                    const coverFile =
                        coverInput
                            ? coverInput.files[0]
                            : null;

                    const avatarFile =
                        avatarInput
                            ? avatarInput.files[0]
                            : null;


                    if (!coverFile && !avatarFile) {

                        showMessage(
                            "Please select a cover or profile image.",
                            false
                        );

                        return;
                    }


                    const formData =
                        new FormData();


                    if (avatarFile) {

                        formData.append(
                            "profile_image",
                            avatarFile
                        );

                    }


                    if (coverFile) {

                        formData.append(
                            "cover_image",
                            coverFile
                        );

                    }


                    saveImages.disabled = true;
                    saveImages.textContent = "Uploading...";


                    try {

                        const response =
                            await fetch(
                                "/admin/profile/upload-images",
                                {
                                    method: "POST",
                                    body: formData
                                }
                            );


                        const result =
                            await response.json();


                        if (!response.ok) {

                            throw new Error(
                                result.message ||
                                "Upload failed."
                            );

                        }


                        if (result.success) {

                            showMessage(
                                result.message,
                                true
                            );


                            /*
                            * Reload after successful upload
                            * so saved images come directly
                            * from the server/database.
                            */

                            setTimeout(
                                function () {

                                    window.location.reload();

                                },
                                800
                            );

                        }


                    } catch (error) {

                        showMessage(
                            error.message,
                            false
                        );

                    } finally {

                        saveImages.disabled = false;
                        saveImages.textContent =
                            "Save Images";

                    }

                }
            );

        }


    /* =====================================================
   REMOVE COVER IMAGE
   ===================================================== */

const removeCover =
    document.getElementById("removeCover");


if (removeCover) {

    removeCover.addEventListener(
        "click",
        async function () {

            const confirmed =
                confirm(
                    "Are you sure you want to remove the cover image?"
                );


            if (!confirmed) {
                return;
            }


            removeCover.disabled = true;
            removeCover.textContent = "Removing...";


            try {

                const response =
                    await fetch(
                        "/admin/profile/remove-cover",
                        {
                            method: "POST"
                        }
                    );


                const result =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.message ||
                        "Unable to remove cover."
                    );

                }


                if (result.success) {

                    showMessage(
                        result.message,
                        true
                    );


                    setTimeout(
                        function () {

                            window.location.reload();

                        },
                        700
                    );

                }


            } catch (error) {

                showMessage(
                    error.message,
                    false
                );

            } finally {

                removeCover.disabled = false;
                removeCover.textContent =
                    "🗑 Remove Cover";

            }

        }
    );

}

    /* =====================================================
       MESSAGE
       ===================================================== */

    function showMessage(message, success) {

        const messageBox =
            document.getElementById(
                "uploadMessage"
            );

        if (!messageBox) {
            return;
        }


        messageBox.textContent =
            message;

        messageBox.style.color =
            success
                ? "#16a34a"
                : "#dc2626";


        setTimeout(function () {

            messageBox.textContent = "";

        }, 3000);

    }

});