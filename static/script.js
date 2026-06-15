const token = localStorage.getItem("token");

if (!token) {

    window.location.replace(
        "http://127.0.0.1:8000/login-page"
    );

}
 let currentRiskFilter = "all";
async function loadDashboard() {

    const statsResponse = await fetch(
        "http://127.0.0.1:8000/stats"
    );

    const stats = await statsResponse.json();

    document.getElementById(
        "users-count"
    ).innerText = stats.total_users;

    document.getElementById(
        "analyses-count"
    ).innerText = stats.total_analyses;

    document.getElementById(
        "high-risk"
    ).innerText = stats.high_risk;


    const riskResponse = await fetch(
        "http://127.0.0.1:8000/risk-score"
    );

    const risk = await riskResponse.json();

    document.getElementById(
        "risk-score"
    ).innerText = risk.average_score;

}

loadDashboard();
async function loadAlerts() {

    const response = await fetch(
        "http://127.0.0.1:8000/alerts"
    );

    const alerts = await response.json();
const search = document
    .getElementById("alertSearch")
    .value
    .toLowerCase();
    const table = document.getElementById(
        "alerts-table"
    );

    table.innerHTML = "";

   alerts
.filter(alert => {

    const matchesSearch =
        alert.threat_type.toLowerCase().includes(search) ||
        alert.message.toLowerCase().includes(search);

    const matchesRisk =
        currentRiskFilter === "all" ||
        alert.risk === currentRiskFilter;

    return matchesSearch && matchesRisk;
})
.forEach(alert => {

        table.innerHTML += `
        <tr>
            <td>${alert.id}</td>
            <td>${alert.threat_type}</td>
            <td>
    <span class="
       ${alert.risk === 'Critical' ? 'critical-risk' :
  alert.risk === 'High' ? 'high-risk' :
  alert.risk === 'Medium' ? 'medium-risk' :
  'low-risk'}
    ">
        ${alert.risk}
    </span>
</td>
            <td>${alert.message}</td>
            
<td>
    <span class="
        ${alert.status === 'Resolved'
            ? 'badge bg-success'
            : 'badge bg-danger'}
    ">
        ${alert.status}
    </span>
</td>
<td>
    ${
        alert.status !== 'Resolved'
        ? `
        <button
            class="btn btn-success btn-sm"
            onclick="resolveAlert(${alert.id})"
        >
            Resolve
        </button>
        `
        : ``
    }

    <button
        class="btn btn-danger btn-sm"
        onclick="deleteAlert(${alert.id})"
    >
        Delete
    </button>
</td>
        </tr>
        `;
    });
}

loadAlerts();
async function loadAnalyses() {

    const response = await fetch(
        "http://127.0.0.1:8000/latest-analyses"
    );

    const analyses = await response.json();

    const table = document.getElementById(
        "analyses-table"
    );

    table.innerHTML = "";

    analyses.forEach(item => {

        table.innerHTML += `
        <tr>
            <td>${item.id}</td>
            <td>
    
<span class="
        ${item.risk === 'Critical' ? 'critical-risk' :
          item.risk === 'High' ? 'high-risk' :
          item.risk === 'Medium' ? 'medium-risk' :
          'low-risk'}
    ">
        ${item.risk}
    </span>
</td>
            <td>${item.analysis}</td>
        </tr>
        `;
    });
}

loadAnalyses();
async function loadThreatChart() {

    const response = await fetch(
        "http://127.0.0.1:8000/threat-stats"
    );

    const data = await response.json();

    const ctx = document.getElementById(
        "threatChart"
    );

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: [
                "Brute Force",
                "SQL Injection",
                "XSS",
                "Port Scan",
                "Admin Attack"
            ],
            datasets: [{
                label: "Threat Count",
                data: [
                    data.brute_force,
                    data.sql_injection,
                    data.xss,
                    data.port_scan,
                    data.admin_attack
                ]
            }]
        }
    });
}

loadThreatChart();
async function uploadLog() {

    const fileInput =
        document.getElementById("logFile");

    const file =
        fileInput.files[0];

    if (!file) {

        alert("Please select a file");

        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    const response = await fetch(
        "http://127.0.0.1:8000/upload-log",
        {
            method: "POST",
            body: formData
        }
    );

    const result = await response.json();

    document.getElementById(
        "upload-result"
    ).innerHTML = `
        <div class="alert alert-info">

            <strong>Risk:</strong>
            ${result.risk}

            <br>

            <strong>Score:</strong>
            ${result.score}
            <br>

<strong>Confidence:</strong>
${result.confidence}%

            <br>

            <strong>Analysis:</strong>
            ${result.analysis}
<br><br>

<strong>Threat Analysis:</strong>

<br>

${Object.entries(result.threat_scores || {})
        .sort((a, b) => b[1] - a[1])
.map(([name, score]) =>
`${name}: ${score}%`
)
.join("<br>")}
        </div>
    `;
}
function logout() {

  localStorage.removeItem("token");

    window.location.replace(
        "http://127.0.0.1:8000/login-page"
    );

}
async function loadUsers() {

    const response = await fetch(
        "http://127.0.0.1:8000/users"
    );

    const users = await response.json();
    const search = document
    .getElementById("userSearch")
    .value
    .toLowerCase();

    const table = document.getElementById(
        "users-table"
    );

   table.innerHTML = "";

users
.filter(user =>
    user.username.toLowerCase().includes(search) ||
    user.email.toLowerCase().includes(search)
)
.forEach(user => {

    table.innerHTML += `
        <tr>
            <td>${user.id}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>
    <span class="
        ${user.role === 'admin'
            ? 'badge bg-success'
            : 'badge bg-secondary'}
    ">
        ${user.role}
    </span>
</td>

            <td>
                <button
                    class="btn btn-danger btn-sm"
                    onclick="deleteUser(${user.id})"
                >
                    Delete
                </button>

                <button
                    class="btn btn-warning btn-sm ms-1"
                    onclick="makeAdmin(${user.id})"
                >
                    Admin
                </button>
            </td>

        </tr>
        `;
    });
}

loadUsers();


async function makeAdmin(id) {

    await fetch(
        `http://127.0.0.1:8000/users/${id}/role`,
        {
            method: "PUT"
        }
    );

    loadUsers();
}
async function deleteAlert(id) {

    const confirmDelete =
        confirm("Delete this alert?");

    if (!confirmDelete) {
        return;
    }

    await fetch(
        `http://127.0.0.1:8000/alerts/${id}`,
        {
            method: "DELETE"
        }
    );

    loadAlerts();
}
async function resolveAlert(id) {

    await fetch(
        `http://127.0.0.1:8000/alerts/${id}/resolve`,
        {
            method: "PUT"
        }
    );

    loadAlerts();
}
