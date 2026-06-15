import json
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from apps.core.mixins import ActiveProjectMixin
from apps.properties.models import Property
from .models import Visit, Note, FollowUp
from .forms import VisitForm, NoteForm, FollowUpForm


def get_property(project, slug):
    return get_object_or_404(Property, slug=slug, project=project)


class VisitCreateView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug):
        prop = get_property(self.project, slug)
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.property = prop
            visit.save()
        visits = prop.visits.all()
        return render(request, 'activity/partials/_visit_list.html', {
            'property': prop, 'visits': visits, 'visit_form': VisitForm()
        })


class NoteCreateView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug):
        prop = get_property(self.project, slug)
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.property = prop
            note.save()
        notes = prop.notes.all()
        response = render(request, 'activity/partials/_note_list.html', {
            'property': prop, 'notes': notes, 'note_form': NoteForm()
        })
        response['HX-Trigger'] = json.dumps({'noteCountChanged': notes.count()})
        return response


class NoteDeleteView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug, pk):
        prop = get_property(self.project, slug)
        note = get_object_or_404(Note, pk=pk, property=prop)
        note.delete()
        notes = prop.notes.all()
        response = render(request, 'activity/partials/_note_list.html', {
            'property': prop, 'notes': notes, 'note_form': NoteForm()
        })
        response['HX-Trigger'] = json.dumps({'noteCountChanged': notes.count()})
        return response


class FollowUpCreateView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug):
        prop = get_property(self.project, slug)
        form = FollowUpForm(request.POST)
        if form.is_valid():
            fu = form.save(commit=False)
            fu.property = prop
            fu.save()
        followups = prop.followups.all()
        return render(request, 'activity/partials/_followup_list.html', {
            'property': prop, 'followups': followups, 'followup_form': FollowUpForm()
        })


class FollowUpToggleView(LoginRequiredMixin, ActiveProjectMixin, View):
    def post(self, request, slug, pk):
        prop = get_property(self.project, slug)
        fu = get_object_or_404(FollowUp, pk=pk, property=prop)
        fu.is_done = not fu.is_done
        fu.completed_at = timezone.now() if fu.is_done else None
        fu.save()
        followups = prop.followups.all()
        return render(request, 'activity/partials/_followup_list.html', {
            'property': prop, 'followups': followups, 'followup_form': FollowUpForm()
        })
