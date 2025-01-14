async function updateStoveStatus() {
    try {
        const response = await fetch('/api/stove-status');
        const data = await response.json();
        const statusText = data.status === 1 ? "On" : "Off";

        const isoDate = new Date(data.timestamp);
        const formattedDate = isoDate.toLocaleDateString('sr-RS', { day: '2-digit', month: '2-digit', year: 'numeric' });
        const formattedTime = isoDate.toLocaleTimeString('sr-RS', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });

        document.getElementById('relay-status').innerText = `${statusText}`;
        document.getElementById('relay-status-timestamp').innerText = `Vreme: ${formattedDate} ${formattedTime}`;
    } catch (error) {
        console.error("Error fetching stove status:", error);
    }
}

async function updateTemperature() {
    try {
        const response = await fetch('/api/last-temperature');
        const data = await response.json();

        const isoDate = new Date(data.timestamp);
        const formattedDate = isoDate.toLocaleDateString('sr-RS', { day: '2-digit', month: '2-digit', year: 'numeric' });
        const formattedTime = isoDate.toLocaleTimeString('sr-RS', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });

        document.getElementById('temperature').innerText = data.temperature + "°C";
        document.getElementById('temperature-timestamp').innerText = `Vreme: ${formattedDate} ${formattedTime}`;
    } catch (error) {
        console.error("Error fetching temperature data:", error);
    }
}

async function updateDashboard() {
    try {
        const response = await fetch('/api/current-config');
        const data = await response.json();

        document.getElementById('selected-config').innerText = data.name;
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const settingsModal = document.getElementById('settingsModal');
    const configList = document.getElementById('config-list');

    async function fetchConfigurations() {
        try {
            const response = await fetch('/api/configurations');
            if (!response.ok) throw new Error('Failed to fetch configurations');

            const configs = await response.json();
            populateConfigList(configs);
        } catch (error) {
            console.error('Error fetching configurations:', error);
            alert('Error loading configurations. Please try again later.');
        }
    }

    function populateConfigList(configs) {
        configList.innerHTML = ''; // Clear existing items
        configs.forEach(config => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.setAttribute('data-config-name', config.name);
            listItem.textContent = config.name;
            configList.appendChild(listItem);
        });
    }

    async function updateCurrentConfig(configName) {
        try {
            const response = await fetch('/api/current-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: configName }),
            });

            const data = await response.json();
            if (data.message) {
                console.log(`Configuration updated to: ${configName}`);
                updateDashboard();
                closeSettings();
            } else {
                console.warn('No confirmation message in response');
            }
        } catch (error) {
            console.error('Error updating configuration:', error);
            alert('Failed to update the configuration. Please try again later.');
        }
    }

    function openSettings() {
        fetchConfigurations();
        const bootstrapModal = new bootstrap.Modal(settingsModal);
        bootstrapModal.show();
    }

    function closeSettings() {
        const bootstrapModal = bootstrap.Modal.getInstance(settingsModal);
        if (bootstrapModal) bootstrapModal.hide();
    }

    configList.addEventListener('click', (event) => {
        if (event.target.classList.contains('list-group-item')) {
            const configName = event.target.getAttribute('data-config-name');
            if (configName) updateCurrentConfig(configName);
        }
    });

    document.getElementById('open-settings-icon').addEventListener('click', openSettings);

    async function updateDashboard() {
        try {
            const response = await fetch('/api/current-config');
            const data = await response.json();
            document.getElementById('selected-config').innerText = data.name;
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    async function updateStoveStatus() {
        try {
            const response = await fetch('/api/stove-status');
            const data = await response.json();
            const statusText = data.status === 1 ? 'On' : 'Off';
            document.getElementById('relay-status').innerText = statusText;
            document.getElementById('relay-status-timestamp').innerText = `Vreme: ${new Date(data.timestamp).toLocaleString('sr-RS')}`;
        } catch (error) {
            console.error('Error fetching stove status:', error);
        }
    }

    async function updateTemperature() {
        try {
            const response = await fetch('/api/last-temperature');
            const data = await response.json();
            document.getElementById('temperature').innerText = `${data.temperature}°C`;
            document.getElementById('temperature-timestamp').innerText = `Vreme: ${new Date(data.timestamp).toLocaleString('sr-RS')}`;
        } catch (error) {
            console.error('Error fetching temperature:', error);
        }
    }

    function refreshDashboard() {
        console.log("Refreshed")
        updateTemperature();
        updateStoveStatus();
        updateDashboard();
    }

    setInterval(refreshDashboard, 5000);
    refreshDashboard();
});
