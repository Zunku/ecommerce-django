from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status
# Class for testing our REST API
from rest_framework.test import APIClient
import pytest

@pytest.fixture
def create_collection(api_client):
    # Function to enable adding a parameter to our fixture. You can't add parameters directly to a fixture.
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection

@pytest.fixture
def delete_collection(api_client):
    def do_delete_collection(id):
        return api_client.delete(f'/store/collections/{id}/')
    return do_delete_collection

# Decorator to allow test to change the database
@pytest.mark.django_db
class TestCreateCollection():
    def test_if_user_is_anonymous_returns_401(self):
        # Each test need to have AAA (Arrange, Act, Assert)
        # Arrange
        # In this case is not needed, we are not creating an object here
        
        # Act
        client = APIClient()
        response = client.post('/store/collections/', {'title': 'a'})
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_return_403(self):
        client=APIClient()
        client.force_authenticate(user={})
        response = client.post('/store/collections/', {'title': 'a'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_if_data_is_invalid_return_400(self, authenticate):
        # Fixture to auth user
        client=APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/', {'title': ''})
        
        # test with multiple assertions. A test can have multiple assertions, but with a single responsability
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
        
    # api_client is a fixture
    def test_if_data_is_valid_return_201(self, api_client, create_collection):
        api_client.force_authenticate(user=User(is_staff=True))
        # Fixture with parameters
        response = create_collection({'title':'a'})
        assert response.status_code == status.HTTP_201_CREATED
        # Another option will be to access directly to the created coleccion but that is an implementation, the less our test know about the intern about our system, will be more reliable.
        assert response.data['id'] > 0
        
        
    # Here pytest realizes that you need api_client for create_collection and authenticate. So pytest creates a single api_client for this test, and the same object is inyected in both fixtures
    def test_if_user_is_not_admin_return_403_v2(self, create_collection, authenticate):
        # Arrange
        # Modifying api_client state
        authenticate()
        # Act
        # Creating a collection with the same api_client
        response = create_collection({'title':'a'})
        # Assert 
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
@pytest.mark.django_db
class TestRetrieveCollection():
    def test_if_collection_exists_return_200(self, api_client):
        # Arrange
        # Here we are testing an implementation, despite it breaks the rule, in this case is the best option
        # Software engineer is not black and white, sometimes you need to break the rules.
        collection = baker.make('Collection')
        
        response = api_client.get(f'/store/collections/{collection.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'product_count':0,
        }
    
    def test_if_collection_does_not_exist_return_404(self, api_client):
        response = api_client.get(f'/store/collections/1/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestUpdateCollection():
    def test_if_user_is_anonymous_returns_401(self, api_client):
        collection = baker.make('Collection')
        response = api_client.put(f'/store/collections/{collection.id}/')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_return_403(self, api_client, authenticate):
        collection = baker.make('Collection')

        authenticate()
        response = api_client.put(f'/store/collections/{collection.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_collection_does_not_exist_return_404(self, api_client, authenticate):
        authenticate(True)
        response = api_client.put(f'/store/collections/1/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_if_data_is_invalid_return_400(self, api_client, authenticate):
        collection = baker.make('Collection')
        
        authenticate(True)
        response = api_client.put(f'/store/collections/{collection.id}/', {'title':''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
        
    def test_if_data_is_valid_return_200(self, api_client, authenticate):
        collection = baker.make('Collection')
        
        authenticate(True)
        response = api_client.put(f'/store/collections/{collection.id}/', {'title':'a'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == collection.id
        
@pytest.mark.django_db
class TestDeleteCollection():
    def test_if_user_is_anonymous_returns_401(self, delete_collection):
        collection = baker.make('Collection')
        response = delete_collection(collection.id)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_return_403(self, delete_collection, authenticate):
        collection = baker.make('Collection')

        authenticate()
        response = delete_collection(collection.id)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_collection_does_not_exist_return_404(self, delete_collection, authenticate):
        
        authenticate(True)
        response = delete_collection(1)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_if_collection_was_deleted(self, delete_collection, authenticate):
        collection = baker.make('Collection')
        
        authenticate(True)
        response = delete_collection(collection.id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT