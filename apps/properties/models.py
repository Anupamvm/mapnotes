import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import Project


AREA_UNIT_CHOICES = [
    ('acres', 'Acres'),
    ('guntha', 'Guntha'),
    ('hectare', 'Hectare'),
    ('sqft', 'Square Feet'),
    ('sqmeter', 'Square Meters'),
]

LAND_TYPE_CHOICES = [
    ('agricultural', 'Agricultural'),
    ('na', 'Non-Agricultural (NA)'),
    ('residential', 'Residential'),
    ('commercial', 'Commercial'),
    ('industrial', 'Industrial'),
    ('mixed', 'Mixed'),
]

PRIORITY_CHOICES = [
    ('hot', 'Hot'),
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
    ('rejected', 'Rejected'),
]

STATUS_CHOICES = [
    ('to_visit', 'To Visit'),
    ('visited', 'Visited'),
    ('under_discussion', 'Under Discussion'),
    ('due_diligence', 'Due Diligence'),
    ('negotiating', 'Negotiating'),
    ('purchased', 'Purchased'),
    ('rejected', 'Rejected'),
]

TERRAIN_TYPE_CHOICES = [
    ('flat', 'Flat'),
    ('sloped', 'Sloped'),
    ('hilly', 'Hilly'),
    ('rocky', 'Rocky'),
]

FILE_TYPE_CHOICES = [
    ('photo', 'Photo'),
    ('survey_map', 'Survey Map'),
    ('pdf', 'PDF'),
    ('document', 'Document'),
    ('video', 'Video'),
]


class Property(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='properties')

    # Identity
    name = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=50, unique=True, blank=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)

    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    full_address = models.TextField(blank=True)
    village = models.CharField(max_length=100, blank=True)
    taluka = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True, default='Maharashtra')
    country = models.CharField(max_length=100, blank=True, default='India')

    # Land Info
    total_area = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    area_unit = models.CharField(max_length=20, choices=AREA_UNIT_CHOICES, default='acres')
    land_type = models.CharField(max_length=20, choices=LAND_TYPE_CHOICES, blank=True)

    # Pricing
    asking_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    expected_negotiated_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_per_acre = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    estimated_market_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    # Ownership & Contact
    owner_name = models.CharField(max_length=200, blank=True)
    agent_name = models.CharField(max_length=200, blank=True)
    agent_phone = models.CharField(max_length=20, blank=True)
    alternate_contact = models.CharField(max_length=200, blank=True)

    # Assessment
    investment_score = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='to_visit')

    general_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'properties'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_id} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.reference_id:
            self.reference_id = f"MN-{uuid.uuid4().hex[:6].upper()}"
        if not self.slug:
            base = slugify(f"{self.name}-{self.reference_id}")
            self.slug = base
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('properties:detail', kwargs={'slug': self.slug})

    @property
    def priority_color(self):
        colors = {
            'hot': 'danger', 'high': 'warning', 'medium': 'info',
            'low': 'success', 'rejected': 'secondary',
        }
        return colors.get(self.priority, 'secondary')

    @property
    def marker_color(self):
        colors = {
            'hot': '#ef4444', 'high': '#f97316', 'medium': '#eab308',
            'low': '#22c55e', 'rejected': '#6b7280',
        }
        return colors.get(self.priority, '#3b82f6')

    def last_visit(self):
        return self.visits.order_by('-visit_date').first()


class SiteEvaluation(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='evaluation')

    # Water
    borewell_available = models.BooleanField(null=True, blank=True)
    borewell_depth = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, help_text='Depth in feet')
    water_availability_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    river_nearby = models.BooleanField(default=False)
    lake_nearby = models.BooleanField(default=False)
    dam_nearby = models.BooleanField(default=False)
    water_comments = models.TextField(blank=True)

    # Access
    road_access_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    distance_to_main_road = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='km')
    internal_road_condition = models.CharField(max_length=200, blank=True)
    accessibility_notes = models.TextField(blank=True)

    # Utilities
    electricity_available = models.BooleanField(null=True, blank=True)
    internet_available = models.BooleanField(null=True, blank=True)
    mobile_network_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(5)])

    # Terrain
    terrain_type = models.CharField(max_length=20, choices=TERRAIN_TYPE_CHOICES, blank=True)

    # Environment
    tree_cover_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    scenic_value_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    pollution_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)], help_text='Lower is better')
    noise_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)], help_text='Lower is better')

    # Legal
    title_clear = models.BooleanField(null=True, blank=True)
    mutation_complete = models.BooleanField(null=True, blank=True)
    survey_completed = models.BooleanField(null=True, blank=True)
    encumbrances = models.TextField(blank=True)

    # Future Potential (all /10)
    development_potential_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    tourism_potential_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    farming_potential_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])
    weekend_home_potential_rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])

    def __str__(self):
        return f"Evaluation for {self.property.name}"


class Distance(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='distances')

    highway = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    dam = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    town = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    hospital = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    school = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    railway_station = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    airport = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    industrial_zone = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    future_infrastructure_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'distance info'
        verbose_name_plural = 'distance info'

    def __str__(self):
        return f"Distances for {self.property.name}"


class Attachment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='photo')
    description = models.CharField(max_length=500, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_file_type_display()} for {self.property.name}"

    def is_image(self):
        return self.file_type == 'photo'

    def filename(self):
        import os
        return os.path.basename(self.file.name)
