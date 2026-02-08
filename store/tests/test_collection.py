# Class for testing our REST API
from rest_framework import status
from rest_framework.test import APIClient
import pytest

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