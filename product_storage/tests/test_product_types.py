from http import HTTPStatus

from products.models import ProductType


def test_create_product_type(api_client_with_jwt, product_type_list_url,
                             product_type_data):
    '''Тест проверяет возможность создания типа товара'''

    ProductType.objects.all().delete()
    data = product_type_data

    # Проверяем, что тип создался
    response = api_client_with_jwt.post(product_type_list_url, data,
                                        format='json')
    assert response.status_code == HTTPStatus.CREATED, (
        f'Response: {response.data}')
    assert ProductType.objects.count() == 1

    # Проверяем соответствие полей
    product_type = ProductType.objects.get()
    assert product_type.name == data.get('name')
    assert product_type.description == data.get('description')


def test_read_product_type(api_client_with_jwt, product_type_detail_url,
                           product_type):
    response = api_client_with_jwt.get(product_type_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert response.data.get('name') == product_type.name
    assert response.data.get('description') == product_type.description


def test_update_product_type(api_client_with_jwt, product_type_detail_url,
                             product_type, product_type_patch_data):
    '''Тест проверяет возможность изменения типа товара'''

    data = product_type_patch_data
    response = api_client_with_jwt.patch(product_type_detail_url,
                                         data)
    assert response.status_code == HTTPStatus.OK, f'Response: {response.data}'
    product_type.refresh_from_db()
    assert product_type.name == data.get('name')
    assert product_type.description == (
        data.get('description'))


def test_delete_product_type(api_client_with_jwt, product_type,
                             product_type_detail_url):
    start_count = ProductType.objects.count()

    response = api_client_with_jwt.delete(product_type_detail_url)
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert ProductType.objects.count() == start_count - 1
