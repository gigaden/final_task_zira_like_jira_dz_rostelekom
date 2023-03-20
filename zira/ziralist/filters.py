from django_filters import rest_framework as dj_filters
from .models import Task


class TasklistFilterSet(dj_filters.FilterSet):
    title = dj_filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_active = dj_filters.BooleanFilter(field_name="is_completed")

    order_by_field = "ordering"

    class Meta:
        model = Task
        fields = [
            "name",
            "is_completed",
        ]
