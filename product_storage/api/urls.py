from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProductTypeViewSet, ProductViewSet

router_v1 = SimpleRouter()
router_v1.register('products', ProductViewSet, basename='product')
router_v1.register('product-types', ProductTypeViewSet,
                   basename='product_type')
# router_v1.register(
#     'product-prices', ProductPriceViewSet, basename='product_price')


auth_urls = [path('auth/', include('djoser.urls.jwt'))]


urlpatterns = [
    path('v1/', include(router_v1.urls + auth_urls))
]
