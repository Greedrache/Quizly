from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, RegistrationView, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'), # New registration endpoint
    path('login/', CookieTokenObtainPairView.as_view(), name='login'), # Updated login endpoint to use the custom view that sets cookies
    path('logout/', LogoutView.as_view(), name='logout'), # New logout endpoint to clear cookies
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Optional: Keep the original token endpoint if you want to allow clients to obtain tokens without cookies
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'), # Updated refresh endpoint to use the custom view that reads from cookies
]