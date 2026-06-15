from django import forms
from .models import Visit, Note, FollowUp


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['visit_date', 'notes', 'observations', 'weather_notes', 'agent_present', 'next_action']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'General visit notes...'}),
            'observations': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Specific observations...'}),
            'next_action': forms.Textarea(attrs={'rows': 2, 'placeholder': 'What to do next...'}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['quick_note', 'detailed_note', 'category']
        widgets = {
            'quick_note': forms.TextInput(attrs={'placeholder': 'Quick note...'}),
            'detailed_note': forms.Textarea(attrs={'rows': 4, 'class': 'quill-editor'}),
        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['reminder_date', 'action_type', 'notes']
        widgets = {
            'reminder_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Details...'}),
        }
