from http import HTTPStatus
from random import shuffle
from django.urls import reverse
import pytest
from rest_framework.test import APIClient
from products.models import Product, ProductType, ProductPrice
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_type():
    return ProductType.objects.create(
        name='Электроника', description='Телефоны, планшеты')


@pytest.fixture
def product_type_2():
    return ProductType.objects.create(
        name='Мебель', description='Изысканная мебель на любой вкус')


@pytest.fixture
def product(product_type):
    product = Product.objects.create(name='NokiaPhone',
                                     amount=50,
                                     barcode='12345678',
                                     type=product_type)
    ProductPrice.objects.create(price=500, currency='rub', product=product)
    return product


@pytest.fixture
def test_user_data():
    return {'username': 'test_user', 'password': 'test_pass'}


@pytest.fixture
def user(test_user_data):
    return User.objects.create_user(**test_user_data)


@pytest.fixture
def api_client_with_jwt(user, test_user_data):
    client = APIClient()
    url = reverse('jwt-create')
    response = client.post(url, test_user_data, format='json')
    if response.status_code != HTTPStatus.OK:
        pytest.fail('Не удалось получить JWT токен. Статус-код: '
                    + str(response.status_code))
    token = response.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def product_list(product_type):
    product_list = [Product(
        name=['car', 'laptop', 'banana'][idx],
        type=product_type,
        amount=100 - idx,
        barcode=f'1234567{idx}',
        is_active=bool(idx)
    ) for idx in range(3)]
    Product.objects.bulk_create(product_list)
    products = Product.objects.all()
    ProductPrice.objects.bulk_create(ProductPrice(
        price=100 - idx * 10,
        currency='rub',
        product=product) for idx, product in enumerate(products))
    return products


@pytest.fixture
def product_list_url():
    return reverse('product-list')


@pytest.fixture
def product_detail_url(product):
    return reverse('product-detail', args=(product.id,))

@pytest.fixture
def product_type_list_url():
    return reverse('product_type-list')
