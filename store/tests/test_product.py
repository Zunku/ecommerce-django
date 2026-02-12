from model_bakery import baker
from rest_framework import status
# Class for testing our REST API
import pytest

@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)
    return do_create_product

@pytest.fixture
def update_product(api_client):
    def do_update_product(id, product):
        return api_client.put(f'/store/products/{id}/', product)
    return do_update_product

@pytest.fixture
def delete_product(api_client):
    def do_delete_product(id):
        return api_client.delete(f'/store/products/{id}/')
    return do_delete_product

@pytest.mark.django_db
class TestCreateProduct():
    def test_if_user_is_anonymous_returns_401(self, create_product):
        response = create_product({'title':'a'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_return_403(self, create_product, authenticate):
        authenticate()
        response = create_product({'title':'a'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_valid_return_201(self, authenticate, create_product):
        collection= baker.make('Collection')
        
        authenticate(True)
        response = create_product({'title':'valid', 'inventory':1, 'slug':'valid', 'unit_price':1, 'collection_id':collection.id})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
    
    # parametrize clone the same test several times, changing arguments each time
    # Is not necesary to test if django knows how to validate price, that is already tested by django, I'm doing this only for educational purposes
    # You need to test your own logic, your own validators
    @pytest.mark.parametrize("field, value", [
    ('title', ''),
    ('title', 'a' * 256),
    ('unit_price', 0),
    ('unit_price', 1.123),
    ('unit_price', 1234567),
    ('inventory', 0),
    ('collection_id',0),
    ])
    def test_invalid_fields_return_400(self, create_product, authenticate, field, value):
        collection= baker.make('Collection')
        data = {'title':'valid', 'inventory':1, 'slug':'valid', 'unit_price':1, 'collection_id':collection.id, 'description':'valid'}
        data[field] = value

        authenticate(True)
        response = create_product(data)

        assert response.status_code == 400
        assert field in response.data
        
@pytest.mark.django_db
class TestRetrieveProduct():
    def test_if_product_exists_return_200(self, api_client):
        # Arrange
        # Here we are testing an implementation, despite it breaks the rule, in this case is the best option
        # Software engineer is not black and white, sometimes you need to break the rules.
        product = baker.make('Product')
        
        response = api_client.get(f'/store/products/{product.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': product.id,
            'title': product.title,
            'slug':product.slug,
            'description':product.description,
            'collection_id':product.collection_id,
            'unit_price':product.unit_price,
            'inventory':product.inventory,
            'collection_link':response.data['collection_link'],
            'collection_object':response.data['collection_object'],
            'images':response.data['images'],
            'price_with_tax':response.data['price_with_tax'],
            'collection_title':response.data['collection_title'],
        }
    
    def test_if_product_does_not_exist_return_404(self, api_client):
        response = api_client.get(f'/store/products/1/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestUpdateProduct():
    def test_if_user_is_anonymous_returns_401(self, update_product):
        product = baker.make('Product')
        response = update_product(product.id, {'title':'valid'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_return_403(self, update_product, authenticate):
        product = baker.make('Product')

        authenticate()
        response = update_product(product.id, {'title':'valid'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_product_does_not_exist_return_404(self, update_product, authenticate):
        
        authenticate(True)
        response = update_product(1, {'title':'valid'})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_if_data_is_invalid_return_400(self, update_product, authenticate):
        product = baker.make('Product')
        
        authenticate(True)
        response = update_product(product.id, {'title':''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
        
    def test_if_data_is_valid_return_200(self, update_product, authenticate):
        product = baker.make('Product')
        
        authenticate(True)
        response = update_product(product.id, {'title':'valid', 'inventory':1, 'slug':'valid', 'unit_price':1, 'collection_id':product.collection_id, 'description':'valid'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
        
@pytest.mark.django_db
class TestDeleteProduct():
    def test_if_user_is_anonymous_returns_401(self, delete_product):
        product = baker.make('Product')
        response = delete_product(product.id)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_return_403(self, delete_product, authenticate):
        product = baker.make('Product')

        authenticate()
        response = delete_product(product.id)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_product_does_not_exist_return_404(self, delete_product, authenticate):
        authenticate(True)
        response = delete_product(1)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_if_product_was_deleted(self, delete_product, authenticate):
        product = baker.make('Product')
        
        authenticate(True)
        response = delete_product(product.id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT