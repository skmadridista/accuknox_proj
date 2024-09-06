from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from datetime import timedelta

# Custom pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Signup
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email').lower()  # Case-insensitive email
        password = request.data.get('password')
        name = request.data.get('name')
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(email=email, password=password)
        user.name = name
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

# Login
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email').lower()  # Case-insensitive email
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Search for users by email or name
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            query = query.lower()
            return User.objects.filter(Q(email__iexact=query) | Q(name__icontains=query))
        return User.objects.none()

# Friend request functionalities
@api_view(['POST'])
def send_friend_request(request, user_id):
    to_user = User.objects.get(id=user_id)
    from_user = request.user

    # Limit friend requests to 3 per minute
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_requests = FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count()
    if recent_requests >= 3:
        return Response({"error": "You can only send 3 friend requests per minute"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

    friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        friend_request.accepted = True
        friend_request.save()
        return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
    return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def list_friends(request):
    friends = User.objects.filter(sent_requests__accepted=True, sent_requests__from_user=request.user)
    return Response(UserSerializer(friends, many=True).data)

@api_view(['GET'])
def list_pending_requests(request):
    pending_requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return Response(FriendRequestSerializer(pending_requests, many=True).data)
