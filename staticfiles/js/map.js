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

        // Map click: close any open popup. Never navigate — use Quick Add instead.
        this.map.addListener('click', () => {
            if (this.infoWindow) this.infoWindow.close();
        });

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

        marker._popupHtml = props.popup_html;

        let hoverTimer = null;

        marker.addListener('mouseover', () => {
            hoverTimer = setTimeout(() => {
                this.infoWindow.setContent(props.popup_html);
                this.infoWindow.open(this.map, marker);
            }, 400);
        });

        marker.addListener('mouseout', () => {
            clearTimeout(hoverTimer);
        });

        marker.addListener('click', () => {
            clearTimeout(hoverTimer);
            this.infoWindow.setContent(props.popup_html);
            this.infoWindow.open(this.map, marker);
        });

        this.markers[props.slug] = marker;
    }

    focusMarker(slug) {
        const marker = this.markers[slug];
        if (!marker) return;
        this.infoWindow.close();
        this.map.panTo(marker.getPosition());
        this.map.setZoom(15);
        marker.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(() => marker.setAnimation(null), 1400);
    }

    openMarker(slug) {
        const tryOpen = () => {
            const marker = this.markers[slug];
            if (!marker) return false;
            this.map.panTo(marker.getPosition());
            this.map.setZoom(15);
            this.infoWindow.setContent(marker._popupHtml);
            this.infoWindow.open(this.map, marker);
            return true;
        };
        if (!tryOpen()) {
            // Markers may still be loading — poll briefly
            const iv = setInterval(() => { if (tryOpen()) clearInterval(iv); }, 120);
            setTimeout(() => clearInterval(iv), 4000);
        }
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
