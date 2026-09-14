document.addEventListener("DOMContentLoaded", function () {

    console.log("Student Settings loaded.");

});


function openPasswordModal() {

    document
        .getElementById("passwordModal")
        .classList.add("show");

}


function closePasswordModal() {

    document
        .getElementById("passwordModal")
        .classList.remove("show");

}


function openDeactivationModal() {

    document
        .getElementById("deactivationModal")
        .classList.add("show");

}


function closeDeactivationModal() {

    document
        .getElementById("deactivationModal")
        .classList.remove("show");

}


function openDeletionModal() {

    document
        .getElementById("deletionModal")
        .classList.add("show");

}


function closeDeletionModal() {

    document
        .getElementById("deletionModal")
        .classList.remove("show");

}


function requestDataExport() {

    alert(
        "Data export request feature will be connected to the student data export system."
    );

}