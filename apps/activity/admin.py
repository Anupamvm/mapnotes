from django.contrib import admin
from .models import Visit, Note, FollowUp


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['property', 'visit_date', 'agent_present', 'created_at']
    list_filter = ['agent_present', 'visit_date']
    search_fields = ['property__name', 'notes', 'observations']
    date_hierarchy = 'visit_date'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['property', 'category', 'quick_note', 'created_at']
    list_filter = ['category']
    search_fields = ['property__name', 'quick_note', 'detailed_note']


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['property', 'action_type', 'reminder_date', 'is_done', 'is_overdue']
    list_filter = ['action_type', 'is_done', 'reminder_date']
    list_editable = ['is_done']
    search_fields = ['property__name', 'notes']
    date_hierarchy = 'reminder_date'

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
