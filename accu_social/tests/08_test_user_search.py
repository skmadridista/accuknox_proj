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
def test_user_search(create_user):
    create_user('test@example.com', 'testpassword', 'Test User')
    response = client.get(reverse('user-search'), {'q': 'test', 'ordering': 'email'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['email'] == 'test@example.com'
    assert response.data['results'][0]['name'] == 'Test User'
