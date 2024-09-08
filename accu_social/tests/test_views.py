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
def test_signup(create_user):
    response = client.post(reverse('signup'), {
        'email': 'test@example.com',
        'password': 'testpassword',
        'name': 'Test User'
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='test@example.com').exists()

@pytest.mark.django_db
def test_login(create_user):
    create_user('test@example.com', 'testpassword', 'Test User')
    response = client.post(reverse('login'), {
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_user_search(create_user):
    create_user('test@example.com', 'testpassword', 'Test User')
    response = client.get(reverse('user-search'), {'q': 'test'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['email'] == 'test@example.com'

@pytest.mark.django_db
def test_send_friend_request(create_user, authenticate_user):
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')
    token = authenticate_user('user1@example.com', 'password1')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.post(reverse('send-friend-request', kwargs={'user_id': user2.id}))
    assert response.status_code == status.HTTP_201_CREATED
    assert FriendRequest.objects.filter(from_user=user1, to_user=user2).exists()

@pytest.mark.django_db
def test_accept_friend_request(create_user, authenticate_user):
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')
    friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)
    token = authenticate_user('user2@example.com', 'password2')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.post(reverse('accept-friend-request', kwargs={'request_id': friend_request.id}))
    assert response.status_code == status.HTTP_200_OK
    friend_request.refresh_from_db()
    assert friend_request.accepted

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

@pytest.mark.django_db
def test_list_friends(create_user, authenticate_user):
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')
    FriendRequest.objects.create(from_user=user1, to_user=user2, accepted=True)
    token = authenticate_user('user1@example.com', 'password1')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.get(reverse('list-friends'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['email'] == 'user2@example.com'

@pytest.mark.django_db
def test_list_pending_requests(create_user, authenticate_user):
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')
    FriendRequest.objects.create(from_user=user1, to_user=user2)
    token = authenticate_user('user2@example.com', 'password2')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.get(reverse('list-pending-requests'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['from_user'] == 'user1@example.com'
