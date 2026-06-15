from django.db import models


NOTE_CATEGORY_CHOICES = [
    ('water', 'Water'),
    ('legal', 'Legal'),
    ('access', 'Access'),
    ('price', 'Price'),
    ('agent', 'Agent'),
    ('farming', 'Farming'),
    ('tourism', 'Tourism'),
    ('personal', 'Personal'),
    ('other', 'Other'),
]

ACTION_TYPE_CHOICES = [
    ('call_agent', 'Call Agent'),
    ('revisit', 'Revisit Property'),
    ('request_documents', 'Request Documents'),
    ('negotiate', 'Follow Up on Negotiation'),
    ('other', 'Other'),
]


class Visit(models.Model):
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateField()
    notes = models.TextField(blank=True)
    observations = models.TextField(blank=True)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    weather_notes = models.CharField(max_length=200, blank=True)
    agent_present = models.BooleanField(default=False)
    next_action = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"Visit to {self.property.name} on {self.visit_date}"


class Note(models.Model):
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='notes')
    quick_note = models.CharField(max_length=500)
    detailed_note = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=NOTE_CATEGORY_CHOICES, default='personal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.quick_note[:60]}"


class FollowUp(models.Model):
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='followups')
    reminder_date = models.DateField()
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    notes = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reminder_date']

    def __str__(self):
        return f"{self.get_action_type_display()} for {self.property.name} on {self.reminder_date}"

    def is_overdue(self):
        from django.utils import timezone
        return not self.is_done and self.reminder_date < timezone.now().date()
