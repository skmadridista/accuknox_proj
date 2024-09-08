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
def authenticate_user():
    def _authenticate_user(email, password):
        response = client.post(reverse('login'), {'email': email, 'password': password})
        return response.data['access']
    return _authenticate_user

@pytest.mark.django_db
def test_list_pending_requests(create_user, authenticate_user):
    # Create two users
    user1 = create_user('user1+test@example.com', 'password1', 'User One')
    user2 = create_user('user2+test@example.com', 'password2', 'User Two')

    # Create a friend request from user1 to user2
    FriendRequest.objects.create(from_user=user1, to_user=user2)

    # Authenticate as user2
    token = authenticate_user('user2+test@example.com', 'password2')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Get the list of pending requests for user2
    response = client.get(reverse('list-pending-requests'))

    # Assert that the response is okay, and that the length of the data is 1
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    # Assert that the email of the user who sent the request matches the email of user1
    assert response.data[0]['from_user'] == user1.email
