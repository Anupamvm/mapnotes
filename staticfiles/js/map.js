class MapManager {
    constructor(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        this.markersUrl = container.dataset.markersUrl || '/properties/map/markers/';
        this.newUrl = container.dataset.newUrl || '/properties/new/';
        this.clickToAdd = container.dataset.clickToAdd === 'true';
        this.markers = {};
        this.infoWindow = null;

        this.map = new google.maps.Map(container, {
            zoom: 8,
            center: { lat: 18.5204, lng: 73.8567 },
            mapTypeId: 'hybrid',
            gestureHandling: 'greedy',
            mapTypeControl: true,
            streetViewControl: false,
            fullscreenControl: true,
        });

        this.infoWindow = new google.maps.InfoWindow();
        this.loadMarkers();

        if (this.clickToAdd) {
            this.map.addListener('click', (e) => {
                const lat = e.latLng.lat().toFixed(7);
                const lng = e.latLng.lng().toFixed(7);
                window.location.href = `${this.newUrl}?lat=${lat}&lng=${lng}`;
            });
        }

        // Listen for filter updates
        document.addEventListener('mapMarkersUpdate', (e) => {
            const params = e.detail ? e.detail.params || '' : '';
            this.loadMarkers(params);
        });
    }

    PRIORITY_COLORS = {
        hot: '#ef4444',
        high: '#f97316',
        medium: '#eab308',
        low: '#22c55e',
        rejected: '#6b7280',
    };

    async loadMarkers(params = '') {
        const url = params ? `${this.markersUrl}?${params}` : this.markersUrl;
        try {
            const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await res.json();
            this.clearMarkers();
            if (data.features) {
                data.features.forEach(f => this.addMarker(f));
            }
        } catch (err) {
            console.error('Map markers load error:', err);
        }
    }

    addMarker(feature) {
        const [lng, lat] = feature.geometry.coordinates;
        const props = feature.properties;

        const marker = new google.maps.Marker({
            position: { lat, lng },
            map: this.map,
            title: props.name,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: props.color || this.PRIORITY_COLORS[props.priority] || '#3b82f6',
                fillOpacity: 0.9,
                strokeColor: '#ffffff',
                strokeWeight: 2,
            },
        });

        marker.addListener('click', () => {
            this.infoWindow.setContent(props.popup_html);
            this.infoWindow.open(this.map, marker);
        });

        this.markers[props.slug] = marker;
    }

    highlightMarker(slug) {
        const marker = this.markers[slug];
        if (!marker) return;
        marker.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(() => marker.setAnimation(null), 1400);
    }

    clearMarkers() {
        Object.values(this.markers).forEach(m => m.setMap(null));
        this.markers = {};
    }

    panTo(lat, lng) {
        this.map.panTo({ lat, lng });
        this.map.setZoom(14);
    }
}
