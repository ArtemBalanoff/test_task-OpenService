from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Product, ProductPrice, ProductType

admin.site.unregister(Group)


class ProductPriceInLine(admin.StackedInline):
    model = ProductPrice
    can_delete = False
    extra = 1


class ProductInLine(admin.StackedInline):
    model = Product
    can_delete = False
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductPriceInLine,)
    list_display = ('get_short_name', 'get_price', 'amount',
                    'barcode', 'type', 'is_active')
    list_editable = ('amount', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('name', 'barcode')

    @admin.display(description='Название')
    def get_short_name(self, obj):
        return str(obj)

    @admin.display(description='Стоимость')
    def get_price(self, obj):
        return obj.price.price


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = (ProductInLine,)
    list_display = ('get_short_name', 'get_short_description')

    @admin.display(description='Название')
    def get_short_name(self, obj):
        return str(obj)

    @admin.display(description='Описание')
    def get_short_description(self, obj):
        description = obj.description
        return (description[:100] + '...' if len(description) > 100
                else description)


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'currency')
    list_editable = ('price', 'currency')
    list_filter = ('product__type',)
