from django.urls import path
from .views import CookieTokenObtainPairView, RegistrationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('logout/', CookieTokenObtainPairView.as_view(), name='logout'),  # You can implement a logout view to clear the cookie

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # You can implement a custom refresh view to update the cookie as well
]