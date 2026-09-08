document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       PROGRESS BARS
    ========================================================= */

    const progressBars = document.querySelectorAll(
        ".reports-progress-fill"
    );

    progressBars.forEach(function (bar) {

        const value = Number(
            bar.dataset.value || 0
        );

        const total = Number(
            bar.dataset.total || 0
        );

        let percentage = 0;

        if (total > 0) {
            percentage = (value / total) * 100;
        }

        percentage = Math.max(
            0,
            Math.min(percentage, 100)
        );

        setTimeout(function () {

            bar.style.width =
                percentage + "%";

        }, 100);

    });


    /* =========================================================
       ACTIVITY SEARCH
    ========================================================= */

    const activitySearch =
        document.getElementById(
            "activitySearch"
        );

    const activityItems =
        Array.from(
            document.querySelectorAll(
                ".reports-activity-item"
            )
        );

    const activitySearchEmpty =
        document.getElementById(
            "activitySearchEmpty"
        );

    const activityCount =
        document.getElementById(
            "activityCount"
        );


    function filterActivities() {

        const searchValue =
            activitySearch
                ? activitySearch.value
                    .trim()
                    .toLowerCase()
                : "";

        let visibleCount = 0;


        activityItems.forEach(function (item) {

            const searchText =
                (
                    item.dataset.search ||
                    item.textContent ||
                    ""
                ).toLowerCase();


            const matches =
                searchText.includes(
                    searchValue
                );


            if (matches) {

                item.classList.remove(
                    "activity-hidden"
                );

                visibleCount++;

            } else {

                item.classList.add(
                    "activity-hidden"
                );

            }

        });


        if (activitySearchEmpty) {

            if (
                activityItems.length > 0 &&
                visibleCount === 0
            ) {

                activitySearchEmpty.style.display =
                    "flex";

            } else {

                activitySearchEmpty.style.display =
                    "none";

            }

        }


        if (activityCount) {

            activityCount.textContent =
                visibleCount + " activities";

        }

    }


    if (activitySearch) {

        activitySearch.addEventListener(
            "input",
            filterActivities
        );

    }


    /* =========================================================
       PERIOD FILTER
    ========================================================= */

    const periodFilter =
        document.getElementById(
            "reportPeriodFilter"
        );

    /*
       The report data itself is already prepared by Flask.

       This dropdown is kept as the UI control for future
       period-based backend filtering. It does not alter
       database data on the client side.
    */

    if (periodFilter) {

        periodFilter.addEventListener(
            "change",
            function () {

                const selectedPeriod =
                    periodFilter.value;

                document.body.dataset.reportPeriod =
                    selectedPeriod;

            }
        );

    }


    /* =========================================================
       RESET FILTER
    ========================================================= */

    const resetButton =
        document.getElementById(
            "resetReportFilters"
        );


    if (resetButton) {

        resetButton.addEventListener(
            "click",
            function () {

                if (periodFilter) {
                    periodFilter.value = "all";
                }

                if (activitySearch) {
                    activitySearch.value = "";
                }

                document.body.dataset.reportPeriod =
                    "all";

                filterActivities();

            }
        );

    }


    /* =========================================================
       EXPORT REPORT
    ========================================================= */

    const exportButton =
        document.getElementById(
            "exportReportBtn"
        );


    function csvEscape(value) {

        if (value === null ||
            value === undefined) {

            return "";

        }

        const text =
            String(value)
                .replace(/"/g, '""');

        return '"' + text + '"';

    }


    function addRow(rows, values) {

        rows.push(
            values
                .map(csvEscape)
                .join(",")
        );

    }


    function exportReport() {

        const rows = [];


        /* -----------------------------------------
           REPORT HEADER
        ----------------------------------------- */

        addRow(
            rows,
            [
                "SIH Academia-Industry Collaboration Portal"
            ]
        );

        addRow(
            rows,
            [
                "Industry Activity Report"
            ]
        );

        addRow(
            rows,
            []
        );


        /* -----------------------------------------
           REQUIREMENTS
        ----------------------------------------- */

        addRow(
            rows,
            [
                "Requirements",
                "Value"
            ]
        );

        addRow(
            rows,
            [
                "Total Requirements",
                "{{ report_data.requirements.total|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Open Requirements",
                "{{ report_data.requirements.open|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Closed Requirements",
                "{{ report_data.requirements.closed|default(0) }}"
            ]
        );


        addRow(
            rows,
            []
        );


        /* -----------------------------------------
           APPLICATIONS
        ----------------------------------------- */

        addRow(
            rows,
            [
                "Applications",
                "Value"
            ]
        );

        addRow(
            rows,
            [
                "Total Applications",
                "{{ report_data.applications.total|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Shortlisted",
                "{{ report_data.applications.shortlisted|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Selected",
                "{{ report_data.applications.selected|default(0) }}"
            ]
        );


        addRow(
            rows,
            []
        );


        /* -----------------------------------------
           COLLABORATIONS
        ----------------------------------------- */

        addRow(
            rows,
            [
                "Collaborations",
                "Value"
            ]
        );

        addRow(
            rows,
            [
                "Total Collaborations",
                "{{ report_data.collaborations.total|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Active",
                "{{ report_data.collaborations.active|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Pending",
                "{{ report_data.collaborations.pending|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Completed",
                "{{ report_data.collaborations.completed|default(0) }}"
            ]
        );


        addRow(
            rows,
            []
        );


        /* -----------------------------------------
           MESSAGES
        ----------------------------------------- */

        addRow(
            rows,
            [
                "Messages",
                "Value"
            ]
        );

        addRow(
            rows,
            [
                "Total Messages",
                "{{ report_data.messages.total|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Sent",
                "{{ report_data.messages.sent|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Received",
                "{{ report_data.messages.received|default(0) }}"
            ]
        );

        addRow(
            rows,
            [
                "Unread",
                "{{ report_data.messages.unread|default(0) }}"
            ]
        );


        /* -----------------------------------------
           CREATE CSV
        ----------------------------------------- */

        const csvContent =
            "\uFEFF" +
            rows.join("\n");


        const blob =
            new Blob(
                [csvContent],
                {
                    type:
                        "text/csv;charset=utf-8;"
                }
            );


        const url =
            URL.createObjectURL(blob);


        const link =
            document.createElement("a");


        link.href = url;

        link.download =
            "industry-report.csv";


        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);

        URL.revokeObjectURL(url);

    }


    if (exportButton) {

        exportButton.addEventListener(
            "click",
            exportReport
        );

    }


    /* =========================================================
       INITIAL STATE
    ========================================================= */

    filterActivities();

});