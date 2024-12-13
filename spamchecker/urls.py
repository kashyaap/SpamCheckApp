from django.urls import path
from .Views.User.profile import  UserProfileAPIView
from .Views.User.userRegistration import UserRegistrationAPIView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
]
