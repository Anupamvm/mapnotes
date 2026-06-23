import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

from .models import Property, SiteEvaluation, Distance, Attachment, MapCardSettings
from .forms import PropertyForm, SiteEvaluationForm, DistanceForm, AttachmentForm, PropertyFilterForm
from .utils import compute_investment_score, fetch_distance_from_home
from .card_config import CARD_FIELDS, FIELD_GROUPS, default_card_fields
from apps.core.mixins import ActiveProjectMixin, HTMXMixin
from apps.core.models import Project
from apps.activity.models import Note


class PropertyListView(LoginRequiredMixin, ActiveProjectMixin, HTMXMixin, ListView):
    model = Property
    template_name = 'properties/list.html'
    htmx_template = 'properties/partials/_property_list_results.html'
    context_object_name = 'properties'
    paginate_by = 30

    def get_queryset(self):
        qs = self.project.properties.select_related('evaluation', 'distances').prefetch_related('visits')
        self.filter_form = PropertyFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            qs = self.filter_form.filter_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = self.filter_form
        ctx['markers_url'] = '/properties/map/markers/'
        return ctx

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if getattr(self.request, 'htmx', False):
            response['HX-Trigger'] = json.dumps({'mapMarkersUpdate': True})
        return response


class PropertyDetailView(LoginRequiredMixin, ActiveProjectMixin, DetailView):
    model = Property
    template_name = 'properties/detail.html'
    context_object_name = 'property'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.project.properties.select_related('evaluation', 'distances').prefetch_related(
            'visits', 'notes', 'followups', 'attachments'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['evaluation_form'] = SiteEvaluationForm(instance=getattr(self.object, 'evaluation', None))
        ctx['distance_form'] = DistanceForm(instance=getattr(self.object, 'distances', None))
        ctx['attachment_form'] = AttachmentForm()
        from apps.activity.forms import VisitForm, NoteForm, FollowUpForm
        ctx['visit_form'] = VisitForm()
        ctx['note_form'] = NoteForm()
        ctx['followup_form'] = FollowUpForm()
        return ctx


class PropertyCreateView(LoginRequiredMixin, ActiveProjectMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/form.html'

    def get_initial(self):
        return {
            'latitude': self.request.GET.get('lat', ''),
            'longitude': self.request.GET.get('lng', ''),
        }

    def form_valid(self, form):
        form.instance.project = self.project
        prop = form.save()

        # Create blank related records
        SiteEvaluation.objects.get_or_create(property=prop)
        Distance.objects.get_or_create(property=prop)

        # Handle evaluation and distance sub-forms
        ev_form = SiteEvaluationForm(self.request.POST, instance=prop.evaluation)
        dist_form = DistanceForm(self.request.POST, instance=prop.distances)
        if ev_form.is_valid():
            ev_form.save()
        if dist_form.is_valid():
            dist_form.save()

        if prop.latitude and prop.longitude:
            km, mins = fetch_distance_from_home(prop.latitude, prop.longitude)
            if km is not None:
                prop.distance_from_home_km = km
                prop.drive_time_minutes = mins
                prop.save(update_fields=['distance_from_home_km', 'drive_time_minutes'])

        messages.success(self.request, f'Property "{prop.name}" created.')
        return redirect(prop.get_absolute_url())


class PropertyUpdateView(LoginRequiredMixin, ActiveProjectMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.project.properties.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        prop = self.object
        SiteEvaluation.objects.get_or_create(property=prop)
        Distance.objects.get_or_create(property=prop)
        ctx['evaluation_form'] = SiteEvaluationForm(
            self.request.POST or None, instance=prop.evaluation
        )
        ctx['distance_form'] = DistanceForm(
            self.request.POST or None, instance=prop.distances
        )
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        prop = form.save()
        ev_form = SiteEvaluationForm(self.request.POST, instance=prop.evaluation)
        dist_form = DistanceForm(self.request.POST, instance=prop.distances)
        if ev_form.is_valid():
            ev_form.save()
        if dist_form.is_valid():
            dist_form.save()

        if prop.latitude and prop.longitude:
            km, mins = fetch_distance_from_home(prop.latitude, prop.longitude)
            if km is not None:
                prop.distance_from_home_km = km
                prop.drive_time_minutes = mins
                prop.save(update_fields=['distance_from_home_km', 'drive_time_minutes'])

        messages.success(self.request, f'Property "{prop.name}" updated.')
        return redirect(prop.get_absolute_url())


class PropertyDeleteView(LoginRequiredMixin, ActiveProjectMixin, DeleteView):
    model = Property
    template_name = 'properties/confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return self.project.properties.all()

    def get_success_url(self):
        return '/properties/'


class MapMarkersView(LoginRequiredMixin, ActiveProjectMixin, View):
    def get(self, request):
        qs = self.project.properties.filter(
            latitude__isnull=False, longitude__isnull=False
        ).select_related('evaluation').prefetch_related('visits')

        filter_form = PropertyFilterForm(request.GET)
        if filter_form.is_valid():
            qs = filter_form.filter_queryset(qs)

        card_settings, _ = MapCardSettings.objects.get_or_create(
            project=self.project,
            defaults={'visible_fields': default_card_fields()}
        )
        visible_fields = card_settings.get_visible()

        features = []
        for p in qs:
            popup_html = render_to_string(
                'properties/partials/_property_card_mini.html',
                {'property': p, 'visible_fields': visible_fields},
                request=request
            )
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(p.longitude), float(p.latitude)],
                },
                'properties': {
                    'id': p.id,
                    'slug': p.slug,
                    'name': p.name,
                    'priority': p.priority,
                    'status': p.status,
                    'color': p.marker_color,
                    'url': p.get_absolute_url(),
                    'popup_html': popup_html,
                },
            })
        return JsonResponse({'type': 'FeatureCollection', 'features': features})


class AttachmentUploadView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug):
        prop = get_object_or_404(self.project.properties, slug=slug)
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            att = form.save(commit=False)
            att.property = prop
            att.save()
        attachments = prop.attachments.all()
        return render(request, 'properties/partials/_attachment_list.html', {
            'property': prop, 'attachments': attachments
        })


class AttachmentDeleteView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug, pk):
        prop = get_object_or_404(self.project.properties, slug=slug)
        att = get_object_or_404(Attachment, pk=pk, property=prop)
        att.file.delete(save=False)
        att.delete()
        attachments = prop.attachments.all()
        return render(request, 'properties/partials/_attachment_list.html', {
            'property': prop, 'attachments': attachments
        })


class MapCardSettingsView(LoginRequiredMixin, ActiveProjectMixin, View):
    def _get_or_create_settings(self):
        obj, _ = MapCardSettings.objects.get_or_create(
            project=self.project,
            defaults={'visible_fields': default_card_fields()}
        )
        return obj

    def get(self, request):
        settings_obj = self._get_or_create_settings()
        visible = set(settings_obj.visible_fields)
        groups = {}
        for group in FIELD_GROUPS:
            groups[group] = [
                {**f, 'checked': f['key'] in visible}
                for f in CARD_FIELDS if f['group'] == group
            ]
        return render(request, 'properties/partials/_map_card_settings.html', {'groups': groups})

    def post(self, request):
        selected = request.POST.getlist('fields')
        valid_keys = {f['key'] for f in CARD_FIELDS}
        selected = [k for k in selected if k in valid_keys]
        settings_obj = self._get_or_create_settings()
        settings_obj.visible_fields = selected
        settings_obj.save()
        resp = HttpResponse(
            '<span class="text-success small"><i class="bi bi-check-circle-fill me-1"></i>Saved</span>'
        )
        resp['HX-Trigger'] = 'mapMarkersUpdate'
        return resp


class PropertyChatView(LoginRequiredMixin, TemplateView):
    template_name = 'properties/property_chat.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projects'] = list(
            Project.objects.filter(is_active=True)
            .values('id', 'name', 'slug', 'is_default')
            .order_by('-year', 'name')
        )
        ctx['projects_json'] = json.dumps(ctx['projects'])
        ctx['active_project_id'] = self.request.session.get('active_project_id')
        return ctx


class RecalculateDistanceView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug):
        prop = get_object_or_404(self.project.properties, slug=slug)
        if not prop.latitude or not prop.longitude:
            return JsonResponse({'error': 'No coordinates set for this property.'}, status=400)
        km, mins = fetch_distance_from_home(prop.latitude, prop.longitude)
        if km is None:
            return JsonResponse({'error': 'Could not fetch distance. Check Google Maps API key.'}, status=502)
        prop.distance_from_home_km = km
        prop.drive_time_minutes = mins
        prop.save(update_fields=['distance_from_home_km', 'drive_time_minutes'])
        return JsonResponse({'distance_km': float(km), 'drive_minutes': mins})


class PropertyQuickCreateView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        project = get_object_or_404(Project, pk=data.get('project_id'))
        request.session['active_project_id'] = project.pk

        prop = Property.objects.create(
            project=project,
            name=data.get('name') or 'Unnamed',
            full_address=data.get('full_address', ''),
            latitude=data.get('latitude') or None,
            longitude=data.get('longitude') or None,
            village=data.get('village', ''),
            total_area=data.get('total_area') or None,
            area_unit=data.get('area_unit', 'acres'),
            land_type=data.get('land_type', 'agricultural'),
            asking_price=data.get('asking_price') or None,
            price_per_acre=data.get('price_per_acre') or None,
            price_per_sqft=data.get('price_per_sqft') or None,
            agent_name=data.get('agent_name', ''),
            agent_phone=data.get('agent_phone', ''),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'to_visit'),
            general_notes=data.get('general_notes', ''),
        )

        # Site Evaluation
        ev_defaults = {
            'water_availability_rating': data.get('water_availability_rating') or None,
            'road_access_rating': data.get('road_access_rating') or None,
            'electricity_available': data.get('electricity_available'),
            'borewell_available': data.get('borewell_available'),
            'river_nearby': bool(data.get('river_nearby')),
            'lake_nearby': bool(data.get('lake_nearby')),
            'dam_nearby': bool(data.get('dam_nearby')),
            'terrain_type': data.get('terrain_type', ''),
            'title_clear': data.get('title_clear'),
            'mutation_complete': data.get('mutation_complete'),
            'survey_completed': data.get('survey_completed'),
            'development_potential_rating': data.get('development_potential_rating') or None,
            'tourism_potential_rating': data.get('tourism_potential_rating') or None,
            'farming_potential_rating': data.get('farming_potential_rating') or None,
            'weekend_home_potential_rating': data.get('weekend_home_potential_rating') or None,
        }
        ev, _ = SiteEvaluation.objects.get_or_create(property=prop)
        for k, v in ev_defaults.items():
            setattr(ev, k, v)
        ev.save()

        # Distances
        dist_data = data.get('distances', {})
        dist, _ = Distance.objects.get_or_create(property=prop)
        for field in ('highway', 'dam', 'town', 'hospital', 'school', 'railway_station', 'airport'):
            val = dist_data.get(field)
            if val is not None:
                setattr(dist, field, val)
        dist.save()

        if data.get('quick_note'):
            Note.objects.create(
                property=prop,
                quick_note=str(data['quick_note'])[:500],
                category='personal',
            )

        if prop.latitude and prop.longitude:
            try:
                km, mins = fetch_distance_from_home(prop.latitude, prop.longitude)
                if km is not None:
                    prop.distance_from_home_km = km
                    prop.drive_time_minutes = mins
                    prop.save(update_fields=['distance_from_home_km', 'drive_time_minutes'])
            except Exception:
                pass

        return JsonResponse({
            'redirect': prop.get_absolute_url(),
            'slug': prop.slug,
            'latitude': float(prop.latitude) if prop.latitude else None,
            'longitude': float(prop.longitude) if prop.longitude else None,
        })


class PropertyUpdateLocationView(LoginRequiredMixin, View):
    def post(self, request, slug):
        prop = get_object_or_404(Property, slug=slug)
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        update_fields = []
        lat = data.get('latitude')
        lng = data.get('longitude')
        if lat is not None:
            prop.latitude = lat
            update_fields.append('latitude')
        if lng is not None:
            prop.longitude = lng
            update_fields.append('longitude')
        if 'full_address' in data and data['full_address']:
            prop.full_address = data['full_address']
            update_fields.append('full_address')

        if update_fields:
            prop.save(update_fields=update_fields)

        if prop.latitude and prop.longitude:
            try:
                km, mins = fetch_distance_from_home(prop.latitude, prop.longitude)
                if km is not None:
                    prop.distance_from_home_km = km
                    prop.drive_time_minutes = mins
                    prop.save(update_fields=['distance_from_home_km', 'drive_time_minutes'])
            except Exception:
                pass

        return JsonResponse({
            'success': True,
            'latitude': float(prop.latitude) if prop.latitude else None,
            'longitude': float(prop.longitude) if prop.longitude else None,
        })


class ResolveMapUrlView(LoginRequiredMixin, View):
    """Follows short/redirect Maps URLs server-side and extracts coordinates."""
    ALLOWED_HOSTS = {'goo.gl', 'maps.app.goo.gl', 'maps.google.com', 'www.google.com', 'google.com'}

    def post(self, request):
        import re
        from urllib.request import urlopen, Request as UReq
        from urllib.error import URLError
        from urllib.parse import urlparse

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        url = data.get('url', '').strip()
        parsed = urlparse(url)
        if not parsed.hostname or parsed.hostname.lstrip('www.') not in {h.lstrip('www.') for h in self.ALLOWED_HOSTS}:
            return JsonResponse({'error': 'Not a recognized Maps URL'}, status=400)

        try:
            req = UReq(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urlopen(req, timeout=6)
            final_url = resp.geturl()
        except (URLError, Exception):
            return JsonResponse({'error': 'Could not resolve URL'}, status=400)

        for pattern in [r'@(-?\d+\.\d+),(-?\d+\.\d+)', r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)', r'[?&]ll=(-?\d+\.\d+),(-?\d+\.\d+)']:
            m = re.search(pattern, final_url)
            if m:
                return JsonResponse({'lat': float(m[1]), 'lng': float(m[2]), 'resolved_url': final_url})

        return JsonResponse({'error': 'Could not extract coordinates', 'resolved_url': final_url}, status=400)
