const API = "http://127.0.0.1:5000";

async function loadChart() {
  const [actual, predicted] = await Promise.all([
    fetch(`${API}/data`).then(r => r.json()),
    fetch(`${API}/predict`).then(r => r.json()),
  ]);

  const month = d => d.slice(0, 7);
  const actualLabels = actual.map(x => month(x.month));
  const futureLabels = predicted.map(x => month(x.month));
  // start the dashed forecast line at the last actual point so the lines connect
  const lastActual = actual[actual.length - 1].value;

  new Chart(document.getElementById("salesChart"), {
    type: "line",
    data: {
      labels: [...actualLabels, ...futureLabels],
      datasets: [
        {
          label: "Actual Sales",
          data: actual.map(x => x.value),
          borderWidth: 2,
        },
        {
          label: "Predicted Sales",
          data: [...Array(actual.length - 1).fill(null), lastActual, ...predicted.map(x => x.value)],
          borderDash: [5, 5],
          borderWidth: 2,
        },
      ],
    },
  });
}

loadChart();
