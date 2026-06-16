CARD_FIELDS = [
    {'key': 'district',                   'label': 'District / Taluka',     'group': 'Location'},
    {'key': 'village',                    'label': 'Village',                'group': 'Location'},
    {'key': 'state',                      'label': 'State',                  'group': 'Location'},
    {'key': 'total_area',                 'label': 'Total Area',             'group': 'Land Info'},
    {'key': 'land_type',                  'label': 'Land Type',              'group': 'Land Info'},
    {'key': 'asking_price',               'label': 'Asking Price',           'group': 'Pricing'},
    {'key': 'expected_negotiated_price',  'label': 'Negotiated Price',       'group': 'Pricing'},
    {'key': 'price_per_acre',             'label': 'Price / Acre',           'group': 'Pricing'},
    {'key': 'price_per_sqft',            'label': 'Price / Sq.ft',          'group': 'Pricing'},
    {'key': 'estimated_market_value',     'label': 'Est. Market Value',      'group': 'Pricing'},
    {'key': 'owner_name',                 'label': 'Owner Name',             'group': 'Contact'},
    {'key': 'agent_name',                 'label': 'Agent Name',             'group': 'Contact'},
    {'key': 'agent_phone',                'label': 'Agent Phone',            'group': 'Contact'},
    {'key': 'investment_score',           'label': 'Investment Score',       'group': 'Assessment'},
    {'key': 'distance_from_home_km',      'label': 'Distance from Home',     'group': 'Assessment'},
    {'key': 'drive_time_minutes',         'label': 'Drive Time',             'group': 'Assessment'},
    {'key': 'last_visit',                 'label': 'Last Visit Date',        'group': 'Activity'},
]

FIELD_GROUPS = ['Location', 'Land Info', 'Pricing', 'Contact', 'Assessment', 'Activity']

DEFAULT_FIELDS = [
    'village', 'district',
    'total_area', 'land_type',
    'asking_price', 'price_per_acre', 'price_per_sqft',
    'distance_from_home_km', 'drive_time_minutes',
    'agent_name',
    'last_visit',
]


def default_card_fields():
    return list(DEFAULT_FIELDS)
