import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from userAuth.models import User, FriendRequest

client = APIClient()

@pytest.fixture
def create_user():
    def _create_user(email, password, name):
        user = User.objects.create_user(email=email, password=password)
        user.name = name
        user.save()
        return user
    return _create_user

@pytest.fixture
def authenticate_user(create_user):
    def _authenticate_user(email, password):
        user = create_user(email, password, "Test User")
        response = client.post(reverse('login'), {'email': email, 'password': password})
        return response.data['access']
    return _authenticate_user

@pytest.mark.django_db
def test_list_pending_requests(create_user, authenticate_user):
    user1 = create_user('user1+test@example.com', 'password1', 'User One')
    user2 = create_user('user2+test@example.com', 'password2', 'User Two')
    FriendRequest.objects.create(from_user=user1, to_user=user2)
    token = authenticate_user('user2+test@example.com', 'password2')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.get(reverse('list-pending-requests'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['from_user'] == 'user1+test@example.com'
