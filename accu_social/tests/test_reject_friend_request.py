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
def test_reject_friend_request(create_user, authenticate_user):
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')
    friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)
    token = authenticate_user('user2@example.com', 'password2')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.post(reverse('reject_friend_request', kwargs={'request_id': friend_request.id}))
    assert response.status_code == status.HTTP_200_OK
    assert not FriendRequest.objects.filter(id=friend_request.id).exists()
