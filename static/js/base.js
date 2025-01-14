async function addNewConfig() {
    try {
        const response = await fetch('/api/configurations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: '', days: [] })
        });

        if (response.ok) {
            const data = await response.json();
            window.location.href = `/config/${data.name}`; // Redirect to the new configuration page
        } else {
            console.error('Failed to add configuration');
        }
    } catch (error) {
        console.error('Error adding configuration:', error);
    }
}
