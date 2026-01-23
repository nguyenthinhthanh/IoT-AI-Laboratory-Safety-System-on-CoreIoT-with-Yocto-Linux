// ==================== WEBSOCKET ====================
var gateway = `ws://${window.location.hostname}/ws`;
var websocket;

window.addEventListener('load', onLoad);

function onLoad(event) {
    initWebSocket();
}

function onOpen(event) {
    console.log('Connection opened');
}

function onClose(event) {
    console.log('Connection closed');
    setTimeout(initWebSocket, 2000);
}

function initWebSocket() {
    console.log('Trying to open a WebSocket connection…');
    websocket = new WebSocket(gateway);
    websocket.onopen = onOpen;
    websocket.onclose = onClose;
    websocket.onmessage = onMessage;
}

function Send_Data(data) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(data);
        console.log("Send:", data);
    } else {
        console.warn("WebSocket is not ready yet.!");
        alert("WebSocket is not connected!");
    }
}

// =================== CHART SCRIPT ====================
let tempChart, humiChart, no2Chart, pm10Chart, pm25Chart;
let labels = [];
let maxPoints = 10;

document.addEventListener("DOMContentLoaded", () => {
  tempChart = new Chart(document.getElementById("tempChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Temperature (°C)",
        data: [],
        borderWidth: 2,
        borderColor: "#ff7a1a",
        tension: 0.3
      }]
    }
  });

  humiChart = new Chart(document.getElementById("humiChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Humidity (%)",
        data: [],
        borderWidth: 2,
        borderColor: "#07a0b5",
        tension: 0.3
      }]
    }
  });

  no2Chart = new Chart(document.getElementById("no2Chart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "NO₂ (ppm)",
        data: [],
        borderWidth: 2,
        borderColor: "#8000ff",
        tension: 0.3
      }]
    }
  });

  pm10Chart = new Chart(document.getElementById("pm10Chart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "PM10 (µg/m³)",
        data: [],
        borderWidth: 2,
        borderColor: "#00b300",
        tension: 0.3
      }]
    }
  });

  pm25Chart = new Chart(document.getElementById("pm25Chart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "PM2.5 (µg/m³)",
        data: [],
        borderWidth: 2,
        borderColor: "#ff6600",
        tension: 0.3
      }]
    }
  });
  
});

function average(arr) {
    if (arr.length === 0) return 0;
    let sum = arr.reduce((a, b) => a + b, 0);
    return (sum / arr.length).toFixed(2);
}

function updateDatas(temp, humi, no2, pm10, pm25) {
  let now = new Date();
  let timeLabel = now.getHours() + ":" + String(now.getMinutes()).padStart(2, '0');

  labels.push(timeLabel);
  tempChart.data.datasets[0].data.push(temp);
  humiChart.data.datasets[0].data.push(humi);
  no2Chart.data.datasets[0].data.push(no2);
  pm10Chart.data.datasets[0].data.push(pm10);
  pm25Chart.data.datasets[0].data.push(pm25);

  if (labels.length > maxPoints) {
    labels.shift();
    tempChart.data.datasets[0].data.shift();
    humiChart.data.datasets[0].data.shift();
    no2Chart.data.datasets[0].data.shift();
    pm10Chart.data.datasets[0].data.shift();
    pm25Chart.data.datasets[0].data.shift();
  }

  tempChart.update();
  humiChart.update();
  no2Chart.update();
  pm10Chart.update();
  pm25Chart.update();

  document.getElementById("avgTemp").textContent = average(tempChart.data.datasets[0].data) + " °C";
  document.getElementById("avgHumi").textContent = average(humiChart.data.datasets[0].data) + " %";
  document.getElementById("avgNo2").textContent = average(no2Chart.data.datasets[0].data) + " ppm";
  document.getElementById("avgPm10").textContent = average(pm10Chart.data.datasets[0].data) + " µg/m³";
  document.getElementById("avgPm25").textContent = average(pm25Chart.data.datasets[0].data) + " µg/m³";

  document.getElementById("lastUpdate").textContent = now.getHours() + ":" + 
                                                    String(now.getMinutes()).padStart(2,'0') + ":" +
                                                    String(now.getSeconds()).padStart(2,'0');
}


function onMessage(event) {
    console.log("Received:", event.data);
    try {
        var data = JSON.parse(event.data);
        // You can add specific handling here if needed (e.g., update status)
        document.getElementById("connectedClients").textContent = data.clients + " devices";
        document.getElementById("tempValue").textContent = data.temperature + " °C";
        document.getElementById("humiValue").textContent = data.humidity + " %";
        document.getElementById("no2Value").textContent = data.no2 + " ppm";
        document.getElementById("pm10Value").textContent = data.pm10 + " µg/m³";
        document.getElementById("pm25Value").textContent = data.pm25 + " µg/m³";

        // document.getElementById("npk-n").textContent = data["NPK-N"] + " mg/kg";
        // document.getElementById("npk-p").textContent = data["NPK-P"] + " mg/kg";
        // document.getElementById("npk-k").textContent = data["NPK-K"] + " mg/kg";

        // Update charts with new data
        updateDatas(data.temperature, data.humidity, data.no2, data.pm10, data.pm25);
    } catch (e) {
        console.warn("Invalid JSON:", event.data);
    }
}


// ==================== UI NAVIGATION ====================
let relayList = [];
let deleteTarget = null;

function showSection(id, event) {
    document.querySelectorAll('.section').forEach(sec => sec.style.display = 'none');
    document.getElementById(id).style.display = id === 'settings' ? 'flex' : 'block';
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    event.currentTarget.classList.add('active');
}


// ==================== HOME GAUGES ====================
window.onload = function () {
    const gaugeTemp = new JustGage({
        id: "gauge_temp",
        value: 26,
        min: -10,
        max: 50,
        donut: true,
        pointer: false,
        gaugeWidthScale: 0.25,
        gaugeColor: "transparent",
        levelColorsGradient: true,
        levelColors: ["#00BCD4", "#4CAF50", "#FFC107", "#F44336"]
    });

    const gaugeHumi = new JustGage({
        id: "gauge_humi",
        value: 60,
        min: 0,
        max: 100,
        donut: true,
        pointer: false,
        gaugeWidthScale: 0.25,
        gaugeColor: "transparent",
        levelColorsGradient: true,
        levelColors: ["#42A5F5", "#00BCD4", "#0288D1"]
    });

    setInterval(() => {
        gaugeTemp.refresh(Math.floor(Math.random() * 15) + 20);
        gaugeHumi.refresh(Math.floor(Math.random() * 40) + 40);
    }, 3000);
};


// ==================== DEVICE FUNCTIONS ====================
function openAddRelayDialog() {
    document.getElementById('addRelayDialog').style.display = 'flex';
}
function closeAddRelayDialog() {
    document.getElementById('addRelayDialog').style.display = 'none';
}
function saveRelay() {
    const name = document.getElementById('relayName').value.trim();
    const gpio = document.getElementById('relayGPIO').value.trim();
    if (!name || !gpio) return alert("Please fill all fields!");
    relayList.push({ id: Date.now(), name, gpio, state: false });
    renderRelays();
    closeAddRelayDialog();
}
function renderRelays() {
    const container = document.getElementById('relayContainer');
    container.innerHTML = "";
    relayList.forEach(r => {
        const card = document.createElement('div');
        card.className = 'device-card';
        card.innerHTML = `
      <div class="device-header">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" 
             stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="4"></rect>
        </svg>
        <h4>${r.name}</h4>
        </div>

        <p class="gpio">GPIO: ${r.gpio}</p>
        <p class="device-time">Last changed: ${r.lastChanged}</p>

        <button class="toggle-btn ${r.state ? 'on' : ''}" onclick="toggleRelay(${r.id})">
        ${r.state ? 'ON' : 'OFF'}
        </button>

        <svg class="delete-icon" onclick="showDeleteDialog(${r.id})" 
            xmlns="http://www.w3.org/2000/svg" width="20" height="20" 
            viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" stroke-width="2" 
            stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6l-1 14H6L5 6" />
            <path d="M10 11v6" />
            <path d="M14 11v6" />
            <path d="M9 6V4h6v2" />
        </svg>
    `;
        container.appendChild(card);
    });
}
function toggleRelay(id) {
    const relay = relayList.find(r => r.id === id);
    if (relay) {
        relay.state = !relay.state;
        const relayJSON = JSON.stringify({
            page: "device",
            value: {
                name: relay.name,
                status: relay.state ? "ON" : "OFF",
                gpio: relay.gpio
            }
        });
        Send_Data(relayJSON);
        renderRelays();
    }
}
function showDeleteDialog(id) {
    deleteTarget = id;
    document.getElementById('confirmDeleteDialog').style.display = 'flex';
}
function closeConfirmDelete() {
    document.getElementById('confirmDeleteDialog').style.display = 'none';
}
function confirmDelete() {
    relayList = relayList.filter(r => r.id !== deleteTarget);
    renderRelays();
    closeConfirmDelete();
}


// ==================== SETTINGS FORM ====================
document.getElementById("settingsForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const ssid = document.getElementById("ssid").value.trim();
    const password = document.getElementById("password").value.trim();
    const token = document.getElementById("token").value.trim();
    const server = document.getElementById("server").value.trim();
    const port = document.getElementById("port").value.trim();

    const settingsJSON = JSON.stringify({
        page: "setting",
        value: {
            ssid: ssid,
            password: password,
            token: token,
            server: server,
            port: port
        }
    });

    Send_Data(settingsJSON);
    alert("Configuration has been sent to the device!");
});