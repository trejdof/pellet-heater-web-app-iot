async function loadConfiguration(configName) {
    try {
        const response = await fetch(`/api/configurations/${configName}`);
        const data = await response.json();

        for (const day in data.days) {
            data.days[day].forEach((entry, index) => {
                document.querySelector(`[name="${day}-temp-${index + 1}"]`).value = entry.temperature || '';
                const startTime = entry.start ? entry.start.slice(0, 5) : '';
                const endTime = entry.end ? entry.end.slice(0, 5) : '';
                document.querySelector(`[name="${day}-start-${index + 1}"]`).value = startTime;
                document.querySelector(`[name="${day}-end-${index + 1}"]`).value = endTime;
            });
        }
    } catch (error) {
        console.error("Error loading configuration:", error);
    }
}

async function saveConfiguration(configName) {
    const formData = new FormData(document.getElementById('config-form'));
    const configData = {};

    for (const [key, value] of formData.entries()) {
        const [day, type, index] = key.split('-');
        if (!configData[day]) configData[day] = [];
        if (!configData[day][index - 1]) configData[day][index - 1] = { temperature: null, start: null, end: null };
        if (type === 'temp') configData[day][index - 1].temperature = parseFloat(value);
        else if (type === 'start') configData[day][index - 1].start = value;
        else if (type === 'end') configData[day][index - 1].end = value;
    }

    try {
        const response = await fetch(`/api/configurations/${configName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });

        if (response.ok) {
            alert("Konfiguracija je uspešno sačuvana!");
        } else {
            alert("Greška pri čuvanju konfiguracije.");
        }
    } catch (error) {
        console.error("Error saving configuration:", error);
        alert("Došlo je do greške.");
    }
}
