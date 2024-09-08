import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from userAuth.models import User

class SignupTestCase(APITestCase):
    @pytest.mark.django_db
    def test_signup(self):
        url = reverse('signup')
        data = {
            'email': 'test_signup@example.com',
            'password': 'testpassword',
            'name': 'Test User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test_signup@example.com').exists())
        
        # Additional debugging
        print(f"Response data: {response.data}")
        print(f"User count: {User.objects.count()}")
        user = User.objects.filter(email='test_signup@example.com').first()
        if user:
            print(f"Created user: {user.email}, {user.name}")
        else:
            print("User not found in database")

if __name__ == '__main__':
    pytest.main()