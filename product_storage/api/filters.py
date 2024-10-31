from django_filters import rest_framework as filters

from products.models import Product


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='icontains')
    min_price = filters.NumberFilter(
        field_name='price__price', lookup_expr='gte')
    max_price = filters.NumberFilter(
        field_name='price__price', lookup_expr='lte')
    date_updated_after = filters.DateTimeFilter(
        field_name='date_updated', lookup_expr='gte')
    date_updated_before = filters.DateTimeFilter(
        field_name='date_updated', lookup_expr='lte')
    is_active = filters.BooleanFilter(field_name='is_active')
    currency = filters.CharFilter(field_name='price__currency',
                                  lookup_expr='iexact')

    class Meta:
        model = Product
        fields = (
            'name', 'min_price', 'max_price', 'is_active',
            'date_updated_after', 'date_updated_before',
            'currency')
