import pytest

from django.urls import reverse

from rest_framework import status

from rest_framework.test import APIClient

from userAuth.models import User, FriendRequest
from userAuth.serializers import UserSerializer



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

def test_list_friends(create_user, authenticate_user):

     user1 = create_user('user1@example.com', 'password1', 'User One')

     user2 = create_user('user2@example.com', 'password2', 'User Two')

     FriendRequest.objects.create(from_user=user1, to_user=user2, accepted=True)

     token = authenticate_user('user1@example.com', 'password1')

     client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

     response = client.get(reverse('list-friends', kwargs={'user_id': user1.id}))

     assert response.status_code == status.HTTP_200_OK

     user2_data = UserSerializer(user2).data
     assert user2_data in response.data
