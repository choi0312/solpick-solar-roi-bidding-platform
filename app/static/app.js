let generationChart = null;

const money = (value) => {
  if (value === null || value === undefined) return "-";
  return Math.round(value).toLocaleString("ko-KR") + "원";
};

const kwh = (value) => {
  if (value === null || value === undefined) return "-";
  return Number(value).toLocaleString("ko-KR") + " kWh";
};

async function loadDefaults() {
  const res = await fetch("/api/defaults");
  const data = await res.json();

  const regionSelect = document.getElementById("region");
  data.regions.forEach((region) => {
    const option = document.createElement("option");
    option.value = region;
    option.textContent = region;
    regionSelect.appendChild(option);
  });

  const userTypeSelect = document.getElementById("user_type");
  data.user_types.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    userTypeSelect.appendChild(option);
  });

  const shadeSelect = document.getElementById("shading_level");
  data.shading_levels.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    shadeSelect.appendChild(option);
  });
}

function collectForm() {
  const budgetValue = document.getElementById("budget_krw").value;

  return {
    region: document.getElementById("region").value,
    user_type: document.getElementById("user_type").value,
    roof_area_m2: Number(document.getElementById("roof_area_m2").value),
    roof_usage_ratio: Number(document.getElementById("roof_usage_ratio").value),
    tilt_deg: Number(document.getElementById("tilt_deg").value),
    azimuth_deg: Number(document.getElementById("azimuth_deg").value),
    shading_level: document.getElementById("shading_level").value,
    monthly_bill_krw: Number(document.getElementById("monthly_bill_krw").value),
    electricity_price_krw_per_kwh: Number(
      document.getElementById("electricity_price_krw_per_kwh").value
    ),
    export_price_krw_per_kwh: 80,
    budget_krw: budgetValue ? Number(budgetValue) : null,
    top_n: 3,
  };
}

function renderKpis(data) {
  const top = data.top_installers[0];

  document.getElementById("capacity").textContent =
    data.baseline.capacity_kwp.toLocaleString("ko-KR") + " kWp";
  document.getElementById("annual-generation").textContent = kwh(
    data.baseline.annual_generation_kwh
  );
  document.getElementById("subsidy").textContent = money(data.best_subsidy.amount_krw);
  document.getElementById("payback").textContent = top?.payback_years
    ? top.payback_years + "년"
    : "-";
}

function renderChart(monthly) {
  const ctx = document.getElementById("generation-chart");

  const labels = monthly.map((row) => row.month + "월");
  const values = monthly.map((row) => row.generation_kwh);

  if (generationChart) {
    generationChart.destroy();
  }

  generationChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "예상 발전량(kWh)",
          data: values,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

function renderInstallers(installers) {
  const list = document.getElementById("installer-list");
  list.innerHTML = "";

  installers.forEach((installer, index) => {
    const div = document.createElement("div");
    div.className = "installer";

    div.innerHTML = `
      <div class="installer-header">
        <div>
          <strong>${index + 1}. ${installer.name}</strong>
          <div class="muted">추천점수 ${installer.score}점 · 보증 ${installer.warranty_years}년 · 평점 ${installer.rating}</div>
        </div>
        <span class="badge">${installer.budget_match ? "예산 적합" : "예산 초과"}</span>
      </div>
      <div class="metrics">
        <div>순설치비<br><strong>${money(installer.net_capex_krw)}</strong></div>
        <div>연간 편익<br><strong>${money(installer.annual_benefit_krw)}</strong></div>
        <div>회수기간<br><strong>${installer.payback_years ?? "-"}년</strong></div>
        <div>연간 발전량<br><strong>${kwh(installer.annual_generation_kwh)}</strong></div>
        <div>지원금<br><strong>${money(installer.subsidy_krw)}</strong></div>
        <div>25년 ROI<br><strong>${installer.roi_25yr_percent ?? "-"}%</strong></div>
      </div>
    `;

    list.appendChild(div);
  });
}

async function analyze(event) {
  event.preventDefault();

  const payload = collectForm();

  const res = await fetch("/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    alert("분석 중 오류가 발생했습니다.\n" + text);
    return;
  }

  const data = await res.json();

  renderKpis(data);
  renderChart(data.baseline.monthly_generation);
  renderInstallers(data.top_installers);
}

window.addEventListener("DOMContentLoaded", async () => {
  await loadDefaults();
  document.getElementById("analysis-form").addEventListener("submit", analyze);
});
