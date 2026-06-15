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
