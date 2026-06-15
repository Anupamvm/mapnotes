// After HTMX updates the property list, sync the map markers
document.addEventListener('htmx:afterRequest', function(e) {
    // Check for the mapMarkersUpdate trigger from the response headers
    const trigger = e.detail.xhr.getResponseHeader('HX-Trigger');
    if (trigger) {
        try {
            const triggers = JSON.parse(trigger);
            if (triggers.mapMarkersUpdate !== undefined && window.mapManager) {
                const form = document.getElementById('filter-form');
                const params = form ? new URLSearchParams(new FormData(form)).toString() : '';
                window.mapManager.loadMarkers(params);
            }
        } catch (err) {}
    }
});
