from django.db.models import Count, Avg
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Property
from .serializers import PropertyMiniSerializer, PropertyDetailSerializer
from .utils import compute_investment_score
from apps.core.models import Project


class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'district', 'land_type']
    search_fields = ['name', 'reference_id', 'village', 'district', 'agent_name', 'full_address']
    ordering_fields = ['created_at', 'asking_price', 'investment_score', 'total_area']

    def get_queryset(self):
        project_id = self.request.session.get('active_project_id')
        if project_id:
            return Property.objects.filter(project_id=project_id).select_related('evaluation', 'distances')
        return Property.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyMiniSerializer
        return PropertyDetailSerializer

    @action(detail=True, methods=['post'], url_path='compute-score')
    def compute_score(self, request, pk=None):
        prop = self.get_object()
        score = compute_investment_score(prop)
        if score is not None:
            prop.investment_score = score
            prop.save(update_fields=['investment_score'])
        return Response({'investment_score': score})


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.session.get('active_project_id')
        if not project_id:
            return Response({'error': 'No active project'}, status=400)
        props = Property.objects.filter(project_id=project_id)
        return Response({
            'total': props.count(),
            'visited': props.filter(
                status__in=['visited', 'under_discussion', 'due_diligence', 'negotiating', 'purchased']
            ).count(),
            'hot_priority': props.filter(priority='hot').count(),
            'under_negotiation': props.filter(status='negotiating').count(),
            'avg_asking_price': props.filter(asking_price__isnull=False).aggregate(v=Avg('asking_price'))['v'],
            'by_status': list(props.values('status').annotate(count=Count('id'))),
            'by_priority': list(props.values('priority').annotate(count=Count('id'))),
            'by_district': list(props.values('district').annotate(count=Count('id')).order_by('-count')[:10]),
        })
