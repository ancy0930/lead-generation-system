import logging
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Case, When, Value, CharField
from django.utils import timezone
from .models import Lead
from .serializers import LeadSerializer

logger = logging.getLogger(__name__)

class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source']
    search_fields = ['name', 'email', 'phone', 'business_type']
    ordering_fields = ['created_at', 'status']

    def get_permissions(self):
        # Prevent spam: Throttle public endpoint, internal needs auth
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'business'):
            return Lead.objects.filter(business=self.request.user.business)
        return Lead.objects.none()

    def perform_create(self, serializer):
        lead = serializer.save()
        logger.info(f"Structured Log: Lead Created", extra={
            'lead_id': lead.id, 
            'business_id': lead.business_id, 
            'action_type': 'lead_created',
            'source': lead.source
        })
        # Note: Celery signal triggers background jobs post_save

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        business_id = self.request.user.business.id if hasattr(self.request.user, 'business') else 0
        cache_key = f"metrics_business_{business_id}"
        
        # Check cache first for optimization (Task 2)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        qs = self.get_queryset()
        total = qs.count()
        status_counts = dict(qs.values_list('status').annotate(count=Count('status')))
        
        converted = status_counts.get('converted', 0)
        conversion_rate = (converted / total * 100) if total > 0 else 0

        leads_today = qs.filter(created_at__date=timezone.now().date()).count()
        
        # Source Mapping (Task 5) Analytics aggregation
        qs_with_category = qs.annotate(
            source_cat=Case(
                When(source='instagram', then=Value('social')),
                When(source='google', then=Value('search')),
                When(source='website', then=Value('direct')),
                default=Value('other'),
                output_field=CharField(),
            )
        )
        top_source_entry = qs_with_category.values('source_cat').annotate(count=Count('id')).order_by('-count').first()
        top_source = top_source_entry['source_cat'] if top_source_entry else "N/A"

        # Avg response time strictly for "contacted" leads with valid first_response_at (Task 1)
        avg_td = qs.filter(status='contacted', first_response_at__isnull=False).aggregate(
            avg_rt=Avg(ExpressionWrapper(F('first_response_at') - F('created_at'), output_field=fields.DurationField()))
        )['avg_rt']
        
        avg_response_time_seconds = avg_td.total_seconds() if avg_td else 0
        avg_response_minutes = round(avg_response_time_seconds / 60, 2)

        data = {
            'total_leads': total,
            'leads_today': leads_today,
            'new_leads': status_counts.get('new', 0),
            'contacted': status_counts.get('contacted', 0),
            'converted': converted,
            'lost': status_counts.get('lost', 0),
            'conversion_rate': round(conversion_rate, 2),
            'top_source_category': top_source,
            'avg_response_time_minutes': avg_response_minutes
        }
        
        # Cache for 60 seconds
        cache.set(cache_key, data, 60)
        return Response(data)
