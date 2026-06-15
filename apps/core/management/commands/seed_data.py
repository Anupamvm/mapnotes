import random
from django.core.management.base import BaseCommand
from apps.core.models import Project
from apps.properties.models import Property, SiteEvaluation, Distance


DISTRICTS = ['Pune', 'Nashik', 'Satara', 'Kolhapur', 'Ratnagiri', 'Sangli', 'Ahmednagar', 'Solapur']
TALUKAS = {
    'Pune': ['Maval', 'Velha', 'Mulshi', 'Bhor', 'Haveli'],
    'Nashik': ['Igatpuri', 'Trimbakeshwar', 'Peint', 'Dindori', 'Niphad'],
    'Satara': ['Wai', 'Patan', 'Khandala', 'Man', 'Jawali'],
    'Kolhapur': ['Panhala', 'Shahuwadi', 'Kagal', 'Radhanagari', 'Bhudargad'],
    'Ratnagiri': ['Dapoli', 'Guhagar', 'Chiplun', 'Khed', 'Rajapur'],
    'Sangli': ['Walwa', 'Shirala', 'Khanapur', 'Atpadi', 'Jat'],
    'Ahmednagar': ['Akole', 'Sangamner', 'Shrirampur', 'Rahata', 'Newasa'],
    'Solapur': ['Mohol', 'Barshi', 'Pandharpur', 'Mangalvedhe', 'Akkalkot'],
}
PRIORITIES = ['hot', 'hot', 'high', 'high', 'medium', 'medium', 'low', 'rejected']
STATUSES = ['to_visit', 'to_visit', 'visited', 'visited', 'under_discussion', 'due_diligence', 'negotiating', 'rejected']
LAND_TYPES = ['agricultural', 'agricultural', 'agricultural', 'na', 'residential', 'mixed']
AGENT_NAMES = ['Rajesh Patil', 'Suresh More', 'Anil Deshmukh', 'Priya Kulkarni', 'Vijay Shinde', 'Manoj Jadhav', '']
AREA_UNITS = ['acres', 'acres', 'acres', 'guntha', 'hectare']

# Maharashtra lat/lng bounds roughly
LAT_MIN, LAT_MAX = 16.0, 21.5
LNG_MIN, LNG_MAX = 73.0, 80.5


class Command(BaseCommand):
    help = 'Seed sample data for development'

    def handle(self, *args, **kwargs):
        # Create a sample project
        project, created = Project.objects.get_or_create(
            name='FarmLand Research 2026',
            defaults={
                'description': 'Sample farmland research project in Maharashtra',
                'project_type': 'agriculture',
                'year': 2026,
            }
        )
        if created:
            self.stdout.write(f'Created project: {project.name}')
        else:
            self.stdout.write(f'Using existing project: {project.name}')

        # Create 25 sample properties
        count = 0
        for i in range(25):
            district = random.choice(DISTRICTS)
            taluka = random.choice(TALUKAS[district])
            village = f"Village {chr(65 + i % 26)}"
            lat = round(random.uniform(LAT_MIN, LAT_MAX), 7)
            lng = round(random.uniform(LNG_MIN, LNG_MAX), 7)
            area = round(random.uniform(1, 50), 2)
            area_unit = random.choice(AREA_UNITS)
            price = round(random.uniform(5, 200) * 100000, 0)
            priority = random.choice(PRIORITIES)
            status = random.choice(STATUSES)
            land_type = random.choice(LAND_TYPES)
            agent = random.choice(AGENT_NAMES)

            prop = Property.objects.create(
                project=project,
                name=f"{village}, {taluka} Plot",
                latitude=lat,
                longitude=lng,
                full_address=f"{village}, {taluka}, {district}, Maharashtra",
                village=village,
                taluka=taluka,
                district=district,
                state='Maharashtra',
                country='India',
                total_area=area,
                area_unit=area_unit,
                land_type=land_type,
                asking_price=price,
                price_per_acre=round(price / area, 0) if area_unit == 'acres' else None,
                priority=priority,
                status=status,
                agent_name=agent,
                agent_phone=f"9{random.randint(100000000,999999999)}" if agent else '',
                general_notes=f"Sample property in {taluka}. {'Good access road.' if random.random() > 0.5 else 'Requires site visit.'}"
            )

            # Evaluation
            SiteEvaluation.objects.create(
                property=prop,
                water_availability_rating=random.randint(2, 10),
                borewell_available=random.choice([True, False, None]),
                borewell_depth=random.randint(100, 400) if random.random() > 0.5 else None,
                river_nearby=random.random() > 0.7,
                lake_nearby=random.random() > 0.7,
                dam_nearby=random.random() > 0.6,
                road_access_rating=random.randint(3, 10),
                distance_to_main_road=round(random.uniform(0.5, 15), 1),
                electricity_available=random.choice([True, False, None]),
                internet_available=random.choice([True, False, None]),
                mobile_network_rating=random.randint(1, 5),
                terrain_type=random.choice(['flat', 'sloped', 'hilly', 'rocky']),
                title_clear=random.choice([True, False, None]),
                mutation_complete=random.choice([True, False, None]),
                development_potential_rating=random.randint(1, 10),
                tourism_potential_rating=random.randint(1, 8),
                farming_potential_rating=random.randint(3, 10),
                weekend_home_potential_rating=random.randint(2, 10),
                scenic_value_rating=random.randint(3, 10),
            )

            # Distances
            Distance.objects.create(
                property=prop,
                highway=round(random.uniform(2, 80), 1),
                town=round(random.uniform(1, 30), 1),
                hospital=round(random.uniform(5, 50), 1),
                school=round(random.uniform(1, 20), 1),
                railway_station=round(random.uniform(5, 100), 1),
                airport=round(random.uniform(30, 300), 1),
            )

            count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {count} sample properties in "{project.name}"'))
        self.stdout.write(self.style.SUCCESS(f'Project slug: {project.slug}'))
