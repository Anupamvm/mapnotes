from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Avg, Q
from django.http import JsonResponse

from .models import Project, SiteSettings
from .mixins import ActiveProjectMixin, HTMXMixin


class AccountSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        ctx = {'site_settings': SiteSettings.get()}
        return render(request, 'core/account_settings.html', ctx)

    def post(self, request):
        action = request.POST.get('action', 'profile')

        if action == 'home_address':
            settings_obj = SiteSettings.get()
            settings_obj.home_address = request.POST.get('home_address', '').strip()
            settings_obj.save(update_fields=['home_address'])
            messages.success(request, 'Home address updated.')
        else:
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save(update_fields=['first_name', 'last_name', 'email'])
            messages.success(request, 'Profile updated successfully.')

        return redirect('core:account-settings')


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'core/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(prop_count=Count('properties')).order_by('-year', 'name')


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'core/project_form.html'
    fields = ['name', 'description', 'project_type', 'year']
    success_url = reverse_lazy('core:project-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['active_project_id'] = self.object.pk
        return response


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'core/project_form.html'
    fields = ['name', 'description', 'project_type', 'year', 'is_active']
    success_url = reverse_lazy('core:project-list')


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'core/project_confirm_delete.html'
    success_url = reverse_lazy('core:project-list')

    def form_valid(self, form):
        if str(self.object.pk) == str(self.request.session.get('active_project_id')):
            del self.request.session['active_project_id']
        return super().form_valid(form)


class ProjectActivateView(LoginRequiredMixin, View):
    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        request.session['active_project_id'] = project.pk
        return redirect('core:dashboard')


class ProjectSetDefaultView(LoginRequiredMixin, View):
    def post(self, request, slug):
        Project.objects.update(is_default=False)
        project = get_object_or_404(Project, slug=slug)
        project.is_default = True
        project.save(update_fields=['is_default'])
        request.session['active_project_id'] = project.pk
        messages.success(request, f'"{project.name}" is now your default map.')
        return redirect('core:project-list')


class DashboardView(LoginRequiredMixin, ActiveProjectMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        props = self.project.properties.all()
        ctx['total_properties'] = props.count()
        ctx['total_visited'] = props.filter(
            status__in=['visited', 'under_discussion', 'due_diligence', 'negotiating', 'purchased']
        ).count()
        ctx['hot_count'] = props.filter(priority='hot').count()
        ctx['negotiating_count'] = props.filter(status='negotiating').count()
        ctx['avg_price'] = props.filter(asking_price__isnull=False).aggregate(v=Avg('asking_price'))['v']
        ctx['by_status'] = list(props.values('status').annotate(count=Count('id')))
        ctx['by_priority'] = list(props.values('priority').annotate(count=Count('id')))
        ctx['by_district'] = list(props.values('district').annotate(count=Count('id')).order_by('-count')[:8])
        ctx['recent_properties'] = props.select_related('evaluation').order_by('-updated_at')[:5]
        return ctx


class DashboardPropsView(LoginRequiredMixin, ActiveProjectMixin, View):
    def get(self, request):
        props = self.project.properties.all()
        filter_type = request.GET.get('filter', 'all')

        if filter_type == 'visited':
            qs = props.filter(status__in=['visited', 'under_discussion', 'due_diligence', 'negotiating', 'purchased'])
            title = 'Visited Properties'
        elif filter_type == 'hot':
            qs = props.filter(priority='hot')
            title = 'Hot Leads'
        elif filter_type == 'negotiating':
            qs = props.filter(status='negotiating')
            title = 'Negotiating'
        else:
            qs = props
            title = 'All Properties'

        properties = qs.select_related('evaluation').order_by('-updated_at')[:20]
        return render(request, 'core/partials/_dashboard_props.html', {
            'properties': properties,
            'filter_type': filter_type,
            'title': title,
        })


class GlobalSearchView(LoginRequiredMixin, ActiveProjectMixin, TemplateView):
    template_name = 'core/search_results.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get('q', '').strip()
        ctx['query'] = q
        if q:
            from apps.properties.models import Property
            ctx['results'] = self.project.properties.filter(
                Q(name__icontains=q) |
                Q(village__icontains=q) |
                Q(district__icontains=q) |
                Q(full_address__icontains=q) |
                Q(agent_name__icontains=q) |
                Q(owner_name__icontains=q) |
                Q(general_notes__icontains=q) |
                Q(notes__quick_note__icontains=q)
            ).distinct()[:30]
        else:
            ctx['results'] = []
        return ctx


class CompareView(LoginRequiredMixin, ActiveProjectMixin, TemplateView):
    template_name = 'core/compare.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ids = self.request.GET.get('ids', '')
        id_list = [i.strip() for i in ids.split(',') if i.strip().isdigit()]
        ctx['properties'] = self.project.properties.filter(
            pk__in=id_list
        ).select_related('evaluation', 'distances').prefetch_related('visits')[:6]
        return ctx
