import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from userAuth.models import User

client = APIClient()

@pytest.fixture
def create_user():
    def _create_user(email, password, name):
        user = User.objects.create_user(email=email, password=password)
        user.name = name
        user.save()
        return user
    return _create_user

@pytest.mark.django_db
def test_login(create_user):
    """
    Test that a user can log in successfully.

    1. Create a new user in the database.
    2. Make a POST request to the login endpoint with the user's email and password.
    3. Check that the response is successful.
    4. Check that the response contains an 'access' key.
    """
    create_user('test_signup@example.com', 'testpassword', 'Test User')
    response = client.post(reverse('login'), {
        'email': 'test_signup@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

if __name__ == '__main__':
    pytest.main()