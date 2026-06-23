from django.urls import path
from . import views
from apps.activity import views as activity_views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='list'),
    path('chat/', views.PropertyChatView.as_view(), name='chat'),
    path('quick-create/', views.PropertyQuickCreateView.as_view(), name='quick-create'),
    path('new/', views.PropertyCreateView.as_view(), name='create'),
    path('map/markers/', views.MapMarkersView.as_view(), name='map-markers'),
    path('map/card-settings/', views.MapCardSettingsView.as_view(), name='map-card-settings'),
    path('resolve-map-url/', views.ResolveMapUrlView.as_view(), name='resolve-map-url'),

    path('<slug:slug>/', views.PropertyDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.PropertyUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.PropertyDeleteView.as_view(), name='delete'),
    path('<slug:slug>/recalculate-distance/', views.RecalculateDistanceView.as_view(), name='recalculate-distance'),
    path('<slug:slug>/update-location/', views.PropertyUpdateLocationView.as_view(), name='update-location'),

    # HTMX activity partials
    path('<slug:slug>/visits/add/', activity_views.VisitCreateView.as_view(), name='visit-add'),
    path('<slug:slug>/notes/add/', activity_views.NoteCreateView.as_view(), name='note-add'),
    path('<slug:slug>/notes/<int:pk>/delete/', activity_views.NoteDeleteView.as_view(), name='note-delete'),
    path('<slug:slug>/followups/add/', activity_views.FollowUpCreateView.as_view(), name='followup-add'),
    path('<slug:slug>/followups/<int:pk>/toggle/', activity_views.FollowUpToggleView.as_view(), name='followup-toggle'),

    # Attachments
    path('<slug:slug>/attachments/upload/', views.AttachmentUploadView.as_view(), name='attachment-upload'),
    path('<slug:slug>/attachments/<int:pk>/delete/', views.AttachmentDeleteView.as_view(), name='attachment-delete'),
]
