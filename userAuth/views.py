from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
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
from rest_framework_simplejwt.tokens import RefreshToken

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
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Search for users by email or name
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            query = query.lower()
            # Check for exact email match
            exact_email_match = User.objects.filter(email__iexact=query)
            if exact_email_match.exists():
                return exact_email_match
            # Check for name substring match
            return User.objects.filter(name__icontains=query)
        return User.objects.none()

# Friend request functionalities
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_friend_request(request, user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return Response({"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

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
@permission_classes([permissions.IsAuthenticated])
def accept_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
        return Response({"error": "Friend request does not exist"}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.to_user == request.user:
        friend_request.accepted = True
        friend_request.save()
        return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
    return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_friends(request, user_id):
    # Fetch the user object using the user_id
    user = get_object_or_404(User, id=user_id)
    
    # Fetch the friends list for the user
    friends = FriendRequest.objects.filter(from_user=user, accepted=True).values_list('to_user', flat=True)
    friends_list = User.objects.filter(id__in=friends)
    
    # Serialize the friends list
    serializer = UserSerializer(friends_list, many=True)
    
    # Return the serialized data
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_pending_requests(request):
    pending_requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return Response(FriendRequestSerializer(pending_requests, many=True).data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id)
        if friend_request.to_user == request.user:
            friend_request.delete()
            return JsonResponse({'status': 'success', 'message': 'Friend request rejected.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'You are not authorized to reject this request.'}, status=403)
    except FriendRequest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Friend request not found.'}, status=404)
