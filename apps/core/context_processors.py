from django.conf import settings
from .models import Project


def google_maps(request):
    return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}


def active_project(request):
    project = None
    project_id = request.session.get('active_project_id')
    if project_id:
        project = Project.objects.filter(pk=project_id).first()
    return {'active_project': project}
