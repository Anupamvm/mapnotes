import datetime
from django.db import models
from django.utils.text import slugify


class SiteSettings(models.Model):
    home_address = models.CharField(
        max_length=500,
        default="Castle Royale Magnifique, A19, Tower 1, 23rd floor, near Joshi gate, Bopodi, Pune 411020, India",
        help_text="Used as origin for travel distance calculations on properties.",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


PROJECT_TYPE_CHOICES = [
    ('agriculture', 'Agriculture / Farmland'),
    ('commercial', 'Commercial'),
    ('residential', 'Residential'),
    ('international', 'International'),
    ('mixed', 'Mixed / Other'),
]


class Project(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='agriculture')
    year = models.PositiveSmallIntegerField(default=datetime.date.today().year)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.name}-{self.year}")
            slug = base
            n = 1
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:project-activate', kwargs={'slug': self.slug})

    @property
    def property_count(self):
        return self.properties.count()
