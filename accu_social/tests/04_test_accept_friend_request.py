import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from userAuth.models import FriendRequest

client = APIClient()

@pytest.fixture
def create_user():
    def _create_user(email, password, name):
        User = get_user_model()
        user = User.objects.create_user(email=email, password=password)
        user.name = name
        user.is_admin = False
        user.save()
        return user
    return _create_user


@pytest.fixture
def authenticate_user():
    def _authenticate_user(email, password):
        response = client.post(reverse('login'), {'email': email, 'password': password})
        return response.data['access']
    return _authenticate_user

@pytest.mark.django_db
def test_accept_friend_request(create_user, authenticate_user):
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')
    friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)
    token = authenticate_user('user2@example.com', 'password2')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.post(reverse('accept-friend-request', kwargs={'request_id': friend_request.id}), format='json')
    assert response.status_code == status.HTTP_200_OK
    friend_request.refresh_from_db()
    assert friend_request.accepted is True
