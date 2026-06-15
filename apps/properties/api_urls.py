from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PropertyViewSet, DashboardStatsView

app_name = 'api'

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', DashboardStatsView.as_view(), name='stats'),
]
