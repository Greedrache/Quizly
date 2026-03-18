from django.urls import path
from .views import CookieTokenObtainPairView, RegistrationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]