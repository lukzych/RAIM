const ecgChart = new Chart(document.getElementById('cv-ECG'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            data: [],
            borderColor: 'oklch(0.65 0.18 250)',
            borderWidth: 1.5,
            pointRadius: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { display: false },
            y: { display: false }
        }
    }
});

const bvpChart = new Chart(document.getElementById('cv-BVP'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            data: [],
            borderColor: 'oklch(0.65 0.18 160)',
            borderWidth: 1.5,
            pointRadius: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { display: false },
            y: { display: false }
        }
    }
});

const source = new EventSource('/stream');

source.onmessage = function(event) {
    const msg = JSON.parse(event.data);

    if (msg.sensor === 'ECG') {
        msg.values.forEach(value => {
            ecgChart.data.labels.push('');
            ecgChart.data.datasets[0].data.push(value);
            if (ecgChart.data.datasets[0].data.length > 700) {
                ecgChart.data.labels.shift();
                ecgChart.data.datasets[0].data.shift();
            }
        });
        ecgChart.update();
    }

    if (msg.sensor === 'BVP') {
        msg.values.forEach(value => {
            bvpChart.data.labels.push('');
            bvpChart.data.datasets[0].data.push(value);
            if (bvpChart.data.datasets[0].data.length > 320) {
                bvpChart.data.labels.shift();
                bvpChart.data.datasets[0].data.shift();
            }
        });
        bvpChart.update();
    }
};