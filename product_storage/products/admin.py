from django.contrib import admin
from .models import Product, ProductType, ProductPrice
from django.contrib.auth.models import Group


admin.site.unregister(Group)


class ProductPriceInLine(admin.StackedInline):
    model = ProductPrice
    can_delete = False
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductPriceInLine,)
    list_display = ('get_short_name', 'get_price', 'amount', 'barcode', 'type')
    list_editable = ('amount',)
    list_filter = ('type',)

    @admin.display(description='Название')
    def get_short_name(self, obj):
        return str(obj)

    @admin.display(description='Стоимость')
    def get_price(self, obj):
        return obj.price.price


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('get_short_name', 'description')

    @admin.display(description='Название')
    def get_short_name(self, obj):
        return str(obj)


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'currency')
    list_editable = ('price', 'currency')
    list_filter = ('product__type',)