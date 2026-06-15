from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project-list'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<slug:slug>/activate/', views.ProjectActivateView.as_view(), name='project-activate'),
    path('projects/<slug:slug>/edit/', views.ProjectUpdateView.as_view(), name='project-edit'),
    path('projects/<slug:slug>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('search/', views.GlobalSearchView.as_view(), name='search'),
    path('compare/', views.CompareView.as_view(), name='compare'),
]
