document.addEventListener("DOMContentLoaded", function () {

    console.log("SIH Admin Reports JS loaded successfully.");

    const data = window.reportsData || {};

    const refreshButton =
        document.getElementById("refreshReports");

    const searchInput =
        document.getElementById("reportSearch");

    const reportCards =
        document.querySelectorAll(".report-card");

    const noReports =
        document.getElementById("noReports");


    /* =====================================================
       BREADCRUMB FIX
       ===================================================== */

    document.querySelectorAll("a, span").forEach(function (element) {

        if (element.textContent.trim() === "Dashboard") {

            const parentText =
                element.parentElement
                    ? element.parentElement.textContent.trim()
                    : "";

            if (parentText.includes("SIH Portal")) {
                element.textContent = "Reports";
            }
        }

    });


    /* =====================================================
       HELPER
       ===================================================== */

    function setValue(id, value) {

        const element =
            document.getElementById(id);

        if (element) {
            element.textContent =
                Number(value || 0).toLocaleString();
        }

    }


    /* =====================================================
       KPI DATA
       ===================================================== */

    setValue(
        "totalStudents",
        data.totalStudents
    );

    setValue(
        "activeIndustries",
        data.activeIndustries
    );

    setValue(
        "industryCollaborations",
        data.industryCollaborations
    );

    setValue(
        "industryOpportunities",
        data.industryOpportunities
    );


    /* =====================================================
       INDUSTRY SNAPSHOT
       ===================================================== */

    setValue(
        "industrySnapshotIndustries",
        data.activeIndustries
    );

    setValue(
        "industryProjects",
        data.industryProjects
    );

    setValue(
        "industrySnapshotOpportunities",
        data.industryOpportunities
    );

    setValue(
        "industrySnapshotCollaborations",
        data.industryCollaborations
    );


    /* =====================================================
       COLLABORATION STATUS
       ===================================================== */

    const collaboration =
        data.collaborationStatus || {};

    setValue(
        "activeCollaborations",
        collaboration.ACTIVE
    );

    setValue(
        "pendingCollaborations",
        collaboration.PENDING
    );

    setValue(
        "completedCollaborations",
        collaboration.COMPLETED
    );

    setValue(
        "rejectedCollaborations",
        collaboration.REJECTED
    );


    /* =====================================================
       OPPORTUNITY STATUS
       ===================================================== */

    const opportunities =
        data.opportunityStatus || {};

    setValue(
        "openOpportunities",
        opportunities.OPEN
    );

    setValue(
        "draftOpportunities",
        opportunities.DRAFT
    );

    setValue(
        "closedOpportunities",
        opportunities.CLOSED
    );

    setValue(
        "cancelledOpportunities",
        opportunities.CANCELLED
    );


    /* =====================================================
       STUDENT BRANCH CHART
       ===================================================== */

    const branchRows =
        document.querySelectorAll(".branch-row");

    const branchData =
        data.studentDistribution || [];

    let totalStudents =
        branchData.reduce(function (sum, item) {

            return sum +
                Number(item.total || 0);

        }, 0);


    branchRows.forEach(function (row, index) {

        const fill =
            row.querySelector(".branch-fill");

        if (!fill) {
            return;
        }

        const count =
            branchData[index]
                ? Number(branchData[index].total || 0)
                : 0;

        const percentage =
            totalStudents > 0
                ? (count / totalStudents) * 100
                : 0;

        setTimeout(function () {

            fill.style.width =
                Math.max(percentage, count > 0 ? 3 : 0) + "%";

        }, 100 + (index * 80));

    });


    /* =====================================================
       REFRESH BUTTON
       ===================================================== */

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            function () {

                if (refreshButton.classList.contains("loading")) {
                    return;
                }

                refreshButton.classList.add("loading");

                const originalText =
                    refreshButton.innerHTML;

                refreshButton.innerHTML =
                    '<span class="refresh-symbol">↻</span> Refreshing...';


                setTimeout(function () {

                    window.location.reload();

                }, 500);

            }
        );

    }


    /* =====================================================
       REPORT SEARCH
       ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                const query =
                    this.value
                        .trim()
                        .toLowerCase();

                let visible =
                    0;


                reportCards.forEach(function (card) {

                    const text =
                        card.textContent
                            .toLowerCase();


                    const match =
                        text.includes(query);


                    card.style.display =
                        match ? "grid" : "none";


                    if (match) {
                        visible++;
                    }

                });


                if (noReports) {

                    noReports.style.display =
                        visible === 0
                            ? "block"
                            : "none";

                }

            }
        );

    }


    /* =====================================================
       REPORT CARD ACTIONS
       ===================================================== */

    reportCards.forEach(function (card) {

        card.addEventListener(
            "click",
            function () {

                const reportType =
                    this.dataset.report;


                let target = null;


                if (reportType === "student") {

                    target =
                        document.querySelector(
                            ".student-panel"
                        );

                }

                else if (reportType === "industry") {

                    target =
                        document.querySelector(
                            ".engagement-list"
                        );

                }

                else if (reportType === "collaboration") {

                    target =
                        document.querySelector(
                            ".status-analytics"
                        );

                }

                else if (reportType === "opportunity") {

                    target =
                        document.querySelector(
                            ".opportunity-grid"
                        );

                }

                else if (reportType === "projects") {

                    target =
                        document.querySelector(
                            "#industryProjects"
                        );

                }

                else if (reportType === "institution") {

                    target =
                        document.querySelector(
                            ".student-panel"
                        );

                }


                if (target) {

                    const panel =
                        target.closest(
                            ".analytics-panel"
                        ) || target;


                    panel.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });


                    panel.animate(
                        [
                            {
                                transform: "scale(1)"
                            },
                            {
                                transform: "scale(1.01)"
                            },
                            {
                                transform: "scale(1)"
                            }
                        ],
                        {
                            duration: 350
                        }
                    );

                }

            }
        );

    });

});