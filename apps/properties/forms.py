from django import forms
from .models import (
    Property, SiteEvaluation, Distance, Attachment,
    AREA_UNIT_CHOICES, LAND_TYPE_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES,
)

BS_INPUT = {'class': 'form-control form-control-sm'}
BS_SELECT = {'class': 'form-select form-select-sm'}
BS_CHECK = {'class': 'form-check-input'}


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['project', 'reference_id', 'slug', 'created_at', 'updated_at', 'investment_score']
        widgets = {
            'latitude': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'e.g. 18.5204'}),
            'longitude': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'e.g. 73.8567'}),
            'full_address': forms.TextInput(attrs={**BS_INPUT, 'id': 'id_full_address', 'placeholder': 'Type address or search with Google Places...'}),
            'general_notes': forms.Textarea(attrs={**BS_INPUT, 'rows': 3}),
            'asking_price': forms.NumberInput(attrs={**BS_INPUT, 'placeholder': '₹'}),
            'expected_negotiated_price': forms.NumberInput(attrs={**BS_INPUT, 'placeholder': '₹'}),
            'price_per_acre': forms.NumberInput(attrs={**BS_INPUT, 'placeholder': '₹ per acre'}),
            'estimated_market_value': forms.NumberInput(attrs={**BS_INPUT, 'placeholder': '₹'}),
            'name': forms.TextInput(attrs={**BS_INPUT}),
            'village': forms.TextInput(attrs={**BS_INPUT}),
            'taluka': forms.TextInput(attrs={**BS_INPUT}),
            'district': forms.TextInput(attrs={**BS_INPUT}),
            'state': forms.TextInput(attrs={**BS_INPUT}),
            'country': forms.TextInput(attrs={**BS_INPUT}),
            'owner_name': forms.TextInput(attrs={**BS_INPUT}),
            'agent_name': forms.TextInput(attrs={**BS_INPUT}),
            'agent_phone': forms.TextInput(attrs={**BS_INPUT}),
            'alternate_contact': forms.TextInput(attrs={**BS_INPUT}),
            'total_area': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any'}),
            'area_unit': forms.Select(attrs={**BS_SELECT}),
            'land_type': forms.Select(attrs={**BS_SELECT}),
            'priority': forms.Select(attrs={**BS_SELECT}),
            'status': forms.Select(attrs={**BS_SELECT}),
        }


class SiteEvaluationForm(forms.ModelForm):
    class Meta:
        model = SiteEvaluation
        exclude = ['property']
        widgets = {
            'water_comments': forms.Textarea(attrs={**BS_INPUT, 'rows': 2}),
            'accessibility_notes': forms.Textarea(attrs={**BS_INPUT, 'rows': 2}),
            'encumbrances': forms.Textarea(attrs={**BS_INPUT, 'rows': 2}),
            'borewell_available': forms.Select(attrs={**BS_SELECT}, choices=[(None, '— Unknown —'), (True, 'Yes'), (False, 'No')]),
            'electricity_available': forms.Select(attrs={**BS_SELECT}, choices=[(None, '— Unknown —'), (True, 'Yes'), (False, 'No')]),
            'internet_available': forms.Select(attrs={**BS_SELECT}, choices=[(None, '— Unknown —'), (True, 'Yes'), (False, 'No')]),
            'terrain_type': forms.Select(attrs={**BS_SELECT}),
            'borewell_depth': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'feet'}),
            'water_availability_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'road_access_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'distance_to_main_road': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'internal_road_condition': forms.TextInput(attrs={**BS_INPUT}),
            'mobile_network_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 5}),
            'tree_cover_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'scenic_value_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'pollution_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'noise_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'development_potential_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'tourism_potential_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'farming_potential_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
            'weekend_home_potential_rating': forms.NumberInput(attrs={**BS_INPUT, 'min': 0, 'max': 10}),
        }


class DistanceForm(forms.ModelForm):
    class Meta:
        model = Distance
        exclude = ['property']
        widgets = {
            'future_infrastructure_notes': forms.Textarea(attrs={**BS_INPUT, 'rows': 3}),
            'highway': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'dam': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'town': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'hospital': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'school': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'railway_station': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'airport': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
            'industrial_zone': forms.NumberInput(attrs={**BS_INPUT, 'step': 'any', 'placeholder': 'km'}),
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'file_type', 'description']


class PropertyFilterForm(forms.Form):
    status = forms.MultipleChoiceField(
        choices=STATUS_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    priority = forms.MultipleChoiceField(
        choices=PRIORITY_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    land_type = forms.MultipleChoiceField(
        choices=LAND_TYPE_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    district = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'District...'}))
    agent_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Agent name...'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min ₹'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max ₹'}))
    min_area = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min area'}))
    max_area = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max area'}))
    water_min = forms.IntegerField(
        required=False, min_value=0, max_value=10,
        widget=forms.NumberInput(attrs={'placeholder': '0-10'})
    )
    has_borewell = forms.BooleanField(required=False)
    title_clear = forms.BooleanField(required=False)
    visited = forms.BooleanField(required=False, label='Has been visited')

    def filter_queryset(self, qs):
        d = self.cleaned_data
        if d.get('status'):
            qs = qs.filter(status__in=d['status'])
        if d.get('priority'):
            qs = qs.filter(priority__in=d['priority'])
        if d.get('land_type'):
            qs = qs.filter(land_type__in=d['land_type'])
        if d.get('district'):
            qs = qs.filter(district__icontains=d['district'])
        if d.get('agent_name'):
            qs = qs.filter(agent_name__icontains=d['agent_name'])
        if d.get('min_price') is not None:
            qs = qs.filter(asking_price__gte=d['min_price'])
        if d.get('max_price') is not None:
            qs = qs.filter(asking_price__lte=d['max_price'])
        if d.get('min_area') is not None:
            qs = qs.filter(total_area__gte=d['min_area'])
        if d.get('max_area') is not None:
            qs = qs.filter(total_area__lte=d['max_area'])
        if d.get('water_min') is not None:
            qs = qs.filter(evaluation__water_availability_rating__gte=d['water_min'])
        if d.get('has_borewell'):
            qs = qs.filter(evaluation__borewell_available=True)
        if d.get('title_clear'):
            qs = qs.filter(evaluation__title_clear=True)
        if d.get('visited'):
            qs = qs.filter(visits__isnull=False).distinct()
        return qs
