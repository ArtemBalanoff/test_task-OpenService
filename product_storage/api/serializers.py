from rest_framework import serializers
from products.models import Product, ProductPrice, ProductType
from products.validators import barcode_regex_validator
from django.core.exceptions import ValidationError


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ('id', 'currency', 'price')


class ProductCreateReadSerializer(serializers.ModelSerializer):
    price = ProductPriceSerializer()

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'amount', 'barcode',
                  'date_updated', 'type', 'is_active')

    def validate_barcode(self, barcode):
        try:
            barcode_regex_validator(barcode)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return barcode

    def create(self, validated_data):
        price_data = validated_data.pop('price')
        product = super().create(validated_data)
        price_data['product'] = product
        ProductPriceSerializer().create(price_data)
        return product


class ProductBulkCreateSerializer(serializers.Serializer):
    products = ProductCreateReadSerializer(many=True)

    def create(self, validated_data):
        validated_data = validated_data.get('products')
        prices_data = [data.pop('price') for data in validated_data]
        product_list = [Product(**el_dict) for el_dict in validated_data]
        products = Product.objects.bulk_create(product_list,
                                               unique_fields=('barcode',))
        prices = [ProductPrice(**price_data, product=product)
                  for price_data, product in zip(prices_data, products)]
        ProductPrice.objects.bulk_create(prices)
        return products

    def to_representation(self, instances):
        return {'products': [ProductCreateReadSerializer(instance).data
                             for instance in instances]}


class ProductUpdateSerializer(ProductCreateReadSerializer):
    '''Используем отдельный сериализатор для patch-запросов,
    чтобы количество можно было изменять только относительно'''

    class Meta(ProductCreateReadSerializer.Meta):
        extra_kwargs = {'amount': {'read_only': True}}

    def update(self, instance, validated_data):
        price_data = validated_data.pop('price')
        ProductPriceSerializer().update(instance.price, price_data)
        return super().update(instance, validated_data)


class ProductUpdateAmountSerializer(serializers.Serializer):
    amount_delta = serializers.IntegerField()

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        amount_delta = attrs.get('amount_delta')
        if instance and instance.amount + amount_delta < 0:
            raise serializers.ValidationError(
                'Количество товара на складе не может стать отрицательным')
        return attrs

    def update(self, instance, validated_data):
        instance.amount += validated_data.get('amount_delta')
        instance.save()
        return instance

    def to_representation(self, instance):
        return ProductCreateReadSerializer(instance).data


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'name', 'description')
