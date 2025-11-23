let currentSort = "";
let currentDir = "asc";

async function loadProjects() {
    let url = "/API/projects";

    // Add sorting for Headcount and Hours
    if (currentSort !== "") {
        url += `?sort=${currentSort}&dir=${currentDir}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    const body = document.getElementById("projectRows");
    body.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");

        // Project name cell (with link)
        let tdName = tr.insertCell();
        tdName.innerHTML = `<a href="/project/${row.project_id}">${row.project_name}</a>`;

        // Department
        let tdDept = tr.insertCell();
        tdDept.textContent = row.department_name;
        
        // Headcount
        let tdHead = tr.insertCell();
        tdHead.textContent = row.headcount;

        // Total hours
        let tdHours = tr.insertCell();
        tdHours.textContent = row.total_hours;
        body.appendChild(tr);

    });
}

function updateArrows() {
    // Clear all arrows (ex. Hours is sorted after headcount, so headcount arrow should be cleared)
    document.getElementById("arrowHeadcount").textContent = "";
    document.getElementById("arrowHours").textContent = "";

    // Apply the correct arrow
    const arrow = currentDir === "asc" ? "▲" : "▼";

    if (currentSort === "headcount") {
        document.getElementById("arrowHeadcount").textContent = arrow;
    } 
    else if (currentSort === "total_hours") {
        document.getElementById("arrowHours").textContent = arrow;
    }
}

// Headcount click event
document.getElementById("sortHeadcount").addEventListener("click", () => {
    if (currentSort === "headcount") {
        currentDir = currentDir === "asc" ? "desc" : "asc"; // toggle
    } else {
        currentSort = "headcount";
        currentDir = "asc";
    }
    updateArrows();
    loadProjects();
});

// Hours click event
document.getElementById("sortHours").addEventListener("click", () => {
    if (currentSort === "total_hours") {
        currentDir = currentDir === "asc" ? "desc" : "asc"; // toggle
    } else {
        currentSort = "total_hours";
        currentDir = "asc";
    }
    updateArrows();
    loadProjects();
});

loadProjects();


