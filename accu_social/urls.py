from django.urls import path, include

urlpatterns = [
    path('api/userAuth/', include('userAuth.urls')),
]
