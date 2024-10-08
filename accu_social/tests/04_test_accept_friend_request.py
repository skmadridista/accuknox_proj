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
    # Create two users who will be involved in the friend request
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')

    # Create a friend request object in the database from user1 to user2
    friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)

    # Authenticate as user2, and save the authentication token
    token = authenticate_user('user2@example.com', 'password2')

    # Set the authentication token in the client's headers
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Post to the accept-friend-request view with the friend request ID
    # This should set the accepted field of the friend request to True
    response = client.post(reverse('accept-friend-request', kwargs={'request_id': friend_request.id}), format='json')

    # Check that the response was successful
    assert response.status_code == status.HTTP_200_OK

    # Check that the accepted field of the friend request is now True
    friend_request.refresh_from_db()
    assert friend_request.accepted is True
