from django.urls import path
from .views import SignupView, LoginView, UserSearchView, send_friend_request, accept_friend_request, list_friends, list_pending_requests, reject_friend_request

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/send/<int:user_id>/', send_friend_request, name='send-friend-request'),
    path('friend-request/accept/<int:request_id>/', accept_friend_request, name='accept-friend-request'),
    path('reject_request/<int:request_id>/', reject_friend_request, name='reject_friend_request'),
    path('friends/', list_friends, name='list-friends'),
    path('friends/<int:user_id>/', list_friends, name='list-friends-by-id'),
    path('pending-requests/', list_pending_requests, name='list-pending-requests'),
]
