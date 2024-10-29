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
                  'date_updated', 'type')

    def validate_barcode(self, barcode):
        try:
            barcode_regex_validator(barcode)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return barcode


class ProductUpdateSerializer(ProductCreateReadSerializer):
    class Meta(ProductCreateReadSerializer.Meta):
        extra_kwargs = {'amount': {'read_only': True}}


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


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'name', 'description')
