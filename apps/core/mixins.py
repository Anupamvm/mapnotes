from django.shortcuts import redirect
from .models import Project


class HTMXMixin:
    htmx_template = None

    def get_template_names(self):
        if getattr(self.request, 'htmx', False) and self.htmx_template:
            return [self.htmx_template]
        return super().get_template_names()


class ActiveProjectMixin:
    def dispatch(self, request, *args, **kwargs):
        project_id = request.session.get('active_project_id')
        if not project_id:
            return redirect('core:project-list')
        try:
            self.project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            del request.session['active_project_id']
            return redirect('core:project-list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = self.project
        return ctx
