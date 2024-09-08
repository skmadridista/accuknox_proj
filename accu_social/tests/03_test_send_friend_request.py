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
def test_send_friend_request(create_user, authenticate_user):
    user1 = create_user('user_sendfrendrequest1@example.com', 'password1', 'User One')
    user2 = create_user('user_sendfrendrequest2@example.com', 'password2', 'User Two')
    token = authenticate_user('user_sendfrendrequest1@example.com', 'password1')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.post(reverse('send-friend-request', kwargs={'user_id': user2.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert FriendRequest.objects.filter(from_user=user1, to_user=user2).exists()

if __name__ == '__main__':
    pytest.main()
