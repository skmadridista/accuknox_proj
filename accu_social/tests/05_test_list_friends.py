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
    # Ensure that test is run in a Django test database
    # This is important because we will be creating objects
    # in the database and then checking that they exist

    # Create two users, user1 and user2
    # These users will be used to test the list-friends API
    user1 = create_user('user1@example.com', 'password1', 'User One')
    user2 = create_user('user2@example.com', 'password2', 'User Two')

    # Create a friend request from user1 to user2
    # This will be used to test the "accepted" field of
    # the list-friends API
    FriendRequest.objects.create(from_user=user1, to_user=user2, accepted=True)

    # Authenticate as user1
    # This is important because the list-friends API requires
    # authentication
    token = authenticate_user('user1@example.com', 'password1')

    # Set the token in the client's headers
    # This is important because the client needs to know
    # that it is authenticated
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Get the list of friends for user1
    # This should return a list containing user2
    response = client.get(reverse('list-friends', kwargs={'user_id': user1.id}))

    # Assert that the response status code is 200
    # This means that the API call was successful
    assert response.status_code == status.HTTP_200_OK

    # Assert that the data returned by the API contains user2
    # This is important because the API should return all
    # of the friends of the user
    user2_data = UserSerializer(user2).data
    assert user2_data in response.data
