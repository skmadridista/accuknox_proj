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
    create_user('test_signup@example.com', 'testpassword', 'Test User')
    response = client.post(reverse('login'), {
        'email': 'test_signup@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    
if __name__ == '__main__':
    pytest.main()