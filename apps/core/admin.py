from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_type', 'year', 'property_count', 'is_active', 'created_at']
    list_filter = ['project_type', 'year', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['slug', 'created_at', 'updated_at']

    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Properties'
