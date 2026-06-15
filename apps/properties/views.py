import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

from .models import Property, SiteEvaluation, Distance, Attachment
from .forms import PropertyForm, SiteEvaluationForm, DistanceForm, AttachmentForm, PropertyFilterForm
from .utils import compute_investment_score
from apps.core.mixins import ActiveProjectMixin, HTMXMixin


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

        features = []
        for p in qs:
            popup_html = render_to_string(
                'properties/partials/_property_card_mini.html',
                {'property': p},
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
