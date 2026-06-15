let formMap = null;
let formMapMarker = null;
let placesAutocomplete = null;

function initPropertyFormMap() {
    const latInput = document.getElementById('id_latitude');
    const lngInput = document.getElementById('id_longitude');
    const mapDiv = document.getElementById('mini-map-form');

    if (!mapDiv) return;

    const lat = parseFloat(latInput.value) || 18.5204;
    const lng = parseFloat(lngInput.value) || 73.8567;
    const hasCoords = latInput.value && lngInput.value;

    formMap = new google.maps.Map(mapDiv, {
        zoom: hasCoords ? 13 : 7,
        center: { lat, lng },
        mapTypeId: 'hybrid',
        gestureHandling: 'greedy',
        streetViewControl: false,
    });

    if (hasCoords) {
        placeFormMarker(lat, lng);
    }

    // Click on form map to set coords
    formMap.addListener('click', (e) => {
        const newLat = e.latLng.lat();
        const newLng = e.latLng.lng();
        latInput.value = newLat.toFixed(7);
        lngInput.value = newLng.toFixed(7);
        placeFormMarker(newLat, newLng);
    });

    // Address autocomplete
    const addressInput = document.getElementById('id_full_address');
    if (addressInput) {
        placesAutocomplete = new google.maps.places.Autocomplete(addressInput, {
            componentRestrictions: { country: 'in' },
            fields: ['geometry', 'formatted_address', 'address_components'],
        });

        placesAutocomplete.addListener('place_changed', () => {
            const place = placesAutocomplete.getPlace();
            if (!place.geometry) return;

            const newLat = place.geometry.location.lat();
            const newLng = place.geometry.location.lng();
            latInput.value = newLat.toFixed(7);
            lngInput.value = newLng.toFixed(7);
            placeFormMarker(newLat, newLng);
            formMap.panTo({ lat: newLat, lng: newLng });
            formMap.setZoom(13);

            // Parse address components
            if (place.address_components) {
                const components = {};
                place.address_components.forEach(c => {
                    c.types.forEach(t => { components[t] = c.long_name; });
                });

                const villageEl = document.getElementById('id_village');
                const talukaEl = document.getElementById('id_taluka');
                const districtEl = document.getElementById('id_district');
                const stateEl = document.getElementById('id_state');

                if (villageEl && (components.locality || components.sublocality_level_1)) {
                    villageEl.value = components.locality || components.sublocality_level_1 || '';
                }
                if (talukaEl && components.administrative_area_level_3) {
                    talukaEl.value = components.administrative_area_level_3;
                }
                if (districtEl && components.administrative_area_level_2) {
                    districtEl.value = components.administrative_area_level_2;
                }
                if (stateEl && components.administrative_area_level_1) {
                    stateEl.value = components.administrative_area_level_1;
                }
            }
        });
    }

    // Keep map in sync when lat/lng fields are manually changed
    [latInput, lngInput].forEach(input => {
        input.addEventListener('change', () => {
            const lat = parseFloat(latInput.value);
            const lng = parseFloat(lngInput.value);
            if (!isNaN(lat) && !isNaN(lng)) {
                placeFormMarker(lat, lng);
                formMap.panTo({ lat, lng });
                formMap.setZoom(13);
            }
        });
    });
}

function placeFormMarker(lat, lng) {
    if (formMapMarker) {
        formMapMarker.setPosition({ lat, lng });
    } else {
        formMapMarker = new google.maps.Marker({
            position: { lat, lng },
            map: formMap,
            draggable: true,
        });
        formMapMarker.addListener('dragend', (e) => {
            document.getElementById('id_latitude').value = e.latLng.lat().toFixed(7);
            document.getElementById('id_longitude').value = e.latLng.lng().toFixed(7);
        });
    }
}
