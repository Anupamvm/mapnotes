from django.contrib import admin
from .models import Property, SiteEvaluation, Distance, Attachment


class SiteEvaluationInline(admin.StackedInline):
    model = SiteEvaluation
    can_delete = False
    extra = 0
    fieldsets = (
        ('Water', {'fields': ('borewell_available', 'borewell_depth', 'water_availability_rating', 'river_nearby', 'lake_nearby', 'dam_nearby', 'water_comments'), 'classes': ('collapse',)}),
        ('Access', {'fields': ('road_access_rating', 'distance_to_main_road', 'internal_road_condition', 'accessibility_notes'), 'classes': ('collapse',)}),
        ('Utilities', {'fields': ('electricity_available', 'internet_available', 'mobile_network_rating'), 'classes': ('collapse',)}),
        ('Terrain & Environment', {'fields': ('terrain_type', 'tree_cover_rating', 'scenic_value_rating', 'pollution_rating', 'noise_rating'), 'classes': ('collapse',)}),
        ('Legal', {'fields': ('title_clear', 'mutation_complete', 'survey_completed', 'encumbrances'), 'classes': ('collapse',)}),
        ('Potential', {'fields': ('development_potential_rating', 'tourism_potential_rating', 'farming_potential_rating', 'weekend_home_potential_rating'), 'classes': ('collapse',)}),
    )


class DistanceInline(admin.TabularInline):
    model = Distance
    extra = 0
    fields = ('highway', 'dam', 'town', 'hospital', 'school', 'railway_station', 'airport', 'industrial_zone', 'future_infrastructure_notes')


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ('file', 'file_type', 'description', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['reference_id', 'name', 'district', 'taluka', 'total_area', 'area_unit',
                    'asking_price', 'priority', 'status', 'investment_score', 'updated_at']
    list_filter = ['status', 'priority', 'land_type', 'district', 'state', 'project']
    search_fields = ['name', 'reference_id', 'village', 'district', 'agent_name', 'owner_name', 'full_address']
    list_editable = ['priority', 'status']
    readonly_fields = ['reference_id', 'slug', 'created_at', 'updated_at']
    inlines = [SiteEvaluationInline, DistanceInline, AttachmentInline]
    date_hierarchy = 'created_at'
    save_on_top = True
    fieldsets = (
        ('Identity', {'fields': ('project', 'name', 'reference_id', 'slug')}),
        ('Location', {'fields': ('latitude', 'longitude', 'full_address', 'village', 'taluka', 'district', 'state', 'country')}),
        ('Land Info', {'fields': ('total_area', 'area_unit', 'land_type')}),
        ('Pricing', {'fields': ('asking_price', 'expected_negotiated_price', 'price_per_acre', 'estimated_market_value')}),
        ('Ownership', {'fields': ('owner_name', 'agent_name', 'agent_phone', 'alternate_contact')}),
        ('Assessment', {'fields': ('investment_score', 'priority', 'status', 'general_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
