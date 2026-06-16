import json
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

_HOME_ADDRESS_FALLBACK = "Castle Royale Magnifique, A19, Tower 1, 23rd floor, near Joshi gate, Bopodi, Pune 411020, India"


def _get_home_address():
    try:
        from apps.core.models import SiteSettings
        return SiteSettings.get().home_address or _HOME_ADDRESS_FALLBACK
    except Exception:
        return _HOME_ADDRESS_FALLBACK


def fetch_distance_from_home(lat, lng):
    """
    Query Google Maps Distance Matrix API for driving distance/time from home.
    Returns (distance_km: float, drive_minutes: int) or (None, None) on failure.
    """
    from django.conf import settings
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    if not api_key or not lat or not lng:
        return None, None

    params = urllib.parse.urlencode({
        'origins': _get_home_address(),
        'destinations': f'{lat},{lng}',
        'mode': 'driving',
        'key': api_key,
    })
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?{params}'

    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        element = data['rows'][0]['elements'][0]
        if element['status'] != 'OK':
            logger.warning("Distance Matrix returned status: %s", element['status'])
            return None, None
        km = round(element['distance']['value'] / 1000, 1)
        minutes = round(element['duration']['value'] / 60)
        return km, minutes
    except Exception:
        logger.exception("Distance Matrix API error for (%s, %s)", lat, lng)
        return None, None


def compute_investment_score(prop):
    ev = getattr(prop, 'evaluation', None)
    if not ev:
        return None

    # Water: max 25 pts
    water = 0
    if ev.water_availability_rating:
        water += ev.water_availability_rating * 1.5
    if ev.river_nearby or ev.lake_nearby or ev.dam_nearby:
        water += 10
    if ev.borewell_available:
        water += 5
    water = min(25, water)

    # Access: max 20 pts
    access = min(20, (ev.road_access_rating or 0) * 2)

    # Legal: max 20 pts
    legal_checks = [ev.title_clear, ev.mutation_complete, ev.survey_completed]
    filled = [x for x in legal_checks if x is not None]
    true_count = sum(1 for x in filled if x)
    legal = (true_count / max(len(filled), 1)) * 20 if filled else 0

    # Potential: max 20 pts
    potential_vals = [
        ev.development_potential_rating, ev.tourism_potential_rating,
        ev.farming_potential_rating, ev.weekend_home_potential_rating,
    ]
    filled_p = [v for v in potential_vals if v is not None]
    potential = (sum(filled_p) / max(len(filled_p), 1) / 10) * 20 if filled_p else 0

    # Utilities: max 15 pts
    utilities = 0
    if ev.electricity_available:
        utilities += 5
    if ev.internet_available:
        utilities += 5
    if ev.mobile_network_rating:
        utilities += (ev.mobile_network_rating / 5) * 5

    total = water + access + legal + potential + utilities
    return round(min(100, total))
