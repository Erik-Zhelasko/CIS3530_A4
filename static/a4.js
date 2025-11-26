document.addEventListener("DOMContentLoaded", () => {
    loadProjectDetails();
    loadEmployeeDropdown();

    document.getElementById("upsertForm").addEventListener("submit", handleUpsert);
});


async function loadProjectDetails() {
    const res = await fetch(`/API/project/${PROJECT_ID}`);
    const data = await res.json();

    document.getElementById("projectTitle").textContent = data.project_name;

    const body = document.getElementById("employeeRows");
    body.innerHTML = "";

    data.employees.forEach(row => {
        const tr = document.createElement("tr");

        const tdName = tr.insertCell();
        tdName.textContent = row.full_name;

        const tdHours = tr.insertCell();
        tdHours.textContent = row.hours;

        body.appendChild(tr);
    });
}

async function loadEmployeeDropdown() {
    const res = await fetch("/API/employees/A4");
    const employees = await res.json();

    const dropdown = document.getElementById("employeeDropdown");
    dropdown.innerHTML = "";

    employees.forEach(emp => {
        const opt = document.createElement("option");
        opt.value = emp.ssn;
        opt.textContent = emp.full_name;
        dropdown.appendChild(opt);
    });
}

async function handleUpsert(event) {
    event.preventDefault();

    const essn = document.getElementById("employeeDropdown").value;
    const hours = document.getElementById("hoursInput").value;

    const res = await fetch("/API/project/upsert", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            project_id: PROJECT_ID,
            essn,
            hours
        })
    });

    const result = await res.json();
    alert(result.message || "Success!");

    // Refresh employee table
    loadProjectDetails();
}
