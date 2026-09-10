/* ============================================
   PLACEMENT CELL - REPORTS
   ============================================ */

document.addEventListener("DOMContentLoaded", function () {

    /* -----------------------------------------
       PRINT REPORT
       ----------------------------------------- */

    const printReportBtn =
        document.getElementById("printReportBtn");

    if (printReportBtn) {

        printReportBtn.addEventListener("click", function () {
            window.print();
        });

    }


    /* -----------------------------------------
       GET TOTAL APPLICATIONS
       ----------------------------------------- */

    let totalApplications = 0;

    const statCards =
        document.querySelectorAll(".report-stat-card");

    statCards.forEach(function (card) {

        const label = card.querySelector("span");
        const value = card.querySelector("strong");

        if (!label || !value) {
            return;
        }

        if (
            label.textContent.trim().toUpperCase() ===
            "APPLICATIONS"
        ) {
            totalApplications =
                parseInt(value.textContent.trim()) || 0;
        }

    });


    /* -----------------------------------------
       PERFORMANCE BARS
       ----------------------------------------- */

    const performanceRows =
        document.querySelectorAll(".performance-row");

    performanceRows.forEach(function (row) {

        const valueElement =
            row.querySelector(".performance-label strong");

        const progressBar =
            row.querySelector(".bar-fill");

        if (!valueElement || !progressBar) {
            return;
        }

        const value =
            parseInt(valueElement.textContent.trim()) || 0;

        let percentage = 0;

        if (totalApplications > 0) {
            percentage =
                (value / totalApplications) * 100;
        }

        percentage =
            Math.min(Math.max(percentage, 0), 100);

        setTimeout(function () {
            progressBar.style.width =
                percentage + "%";
        }, 100);

    });


    /* -----------------------------------------
       APPLICATION STATUS BARS
       ----------------------------------------- */

    const statusItems =
        document.querySelectorAll(".status-report-item");

    statusItems.forEach(function (item) {

        const valueElement =
            item.querySelector(".status-report-top strong");

        const progressBar =
            item.querySelector(".status-progress-fill");

        if (!valueElement || !progressBar) {
            return;
        }

        const value =
            parseInt(valueElement.textContent.trim()) || 0;

        let percentage = 0;

        if (totalApplications > 0) {
            percentage =
                (value / totalApplications) * 100;
        }

        percentage =
            Math.min(Math.max(percentage, 0), 100);

        setTimeout(function () {
            progressBar.style.width =
                percentage + "%";
        }, 100);

    });


    /* -----------------------------------------
       INDUSTRY SELECTION RATES
       ----------------------------------------- */

    const selectionRates =
        document.querySelectorAll(".selection-rate");

    selectionRates.forEach(function (item) {

        const applications =
            parseInt(
                item.getAttribute("data-applications")
            ) || 0;

        const selected =
            parseInt(
                item.getAttribute("data-selected")
            ) || 0;

        const rateElement =
            item.querySelector(".industry-rate-value");

        const progressBar =
            item.querySelector(".mini-progress-fill");

        if (!rateElement || !progressBar) {
            return;
        }

        let rate = 0;

        if (applications > 0) {
            rate =
                (selected / applications) * 100;
        }

        rate =
            Math.min(Math.max(rate, 0), 100);

        rateElement.textContent =
            rate.toFixed(1) + "%";

        setTimeout(function () {

            progressBar.style.width =
                rate + "%";

        }, 100);

    });

});