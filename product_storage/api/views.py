from rest_framework import viewsets, filters
from rest_framework.decorators import action
from .filters import ProductFilter
from products.models import Product, ProductPrice, ProductType
from .serializers import (ProductCreateReadSerializer,
                          ProductUpdateSerializer,
                          ProductTypeSerializer,
                          ProductPriceSerializer,
                          ProductUpdateAmountSerializer)
from rest_framework.response import Response
from http import HTTPStatus
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ('name', 'date_updated', 'price__price')

    def get_queryset(self):
        queryset = Product.objects.select_related('price', 'type')
        ordering = self.request.query_params.get('ordering')
        if ordering:
            ordering = ordering.replace('price', 'price__price')
            queryset = queryset.order_by(ordering)
        return queryset

    def get_serializer_class(self):
        match self.action:
            case 'partial_update':
                return ProductUpdateSerializer
            case _:
                return ProductCreateReadSerializer

    @action(detail=True, methods=('PATCH',))
    def update_amount(self, request, pk):
        instance = self.get_object()
        serializer = ProductUpdateAmountSerializer(instance=instance,
                                                   data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data,
                        status=HTTPStatus.OK)


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.select_related('product')
    serializer_class = ProductPriceSerializer
