from rest_framework import filters
from rest_framework.decorators import action
from .filters import ProductFilter
from products.models import Product, ProductType
from .serializers import (ProductBulkCreateSerializer,
                          ProductCreateReadSerializer,
                          ProductUpdateSerializer,
                          ProductTypeSerializer,
                          ProductUpdateAmountSerializer)
from rest_framework.response import Response
from http import HTTPStatus
from django_filters.rest_framework import DjangoFilterBackend
from .mixins import CRUDWithoutPUT


class ProductViewSet(CRUDWithoutPUT):
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ('name', 'date_updated', 'price__price')

    def get_queryset(self):
        '''Даем возможность обращаться к цене через
        price вместо price__price'''

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

    @action(detail=False, methods=('POST',), url_path='bulk-create')
    def bulk_create(self, request):
        '''Метод для множественного добавления товаров в одном запросе'''

        serializer = ProductBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    @action(detail=True, methods=('PATCH',), url_path='update-amount')
    def update_amount(self, request, pk):
        '''Метод для относительного изменения количества
        товара (+50, -100 и т.д.)'''

        instance = self.get_object()
        serializer = ProductUpdateAmountSerializer(instance=instance,
                                                   data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=HTTPStatus.OK)


class ProductTypeViewSet(CRUDWithoutPUT):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


# class ProductPriceViewSet(CRUDWithoutPUT):
#     queryset = ProductPrice.objects.select_related('product')
#     serializer_class = ProductPriceSerializer
