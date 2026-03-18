from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer, CookieTokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.pk
            }
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            access_token = response.data.get('access')

            # Set the access token in an HttpOnly cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Set to True in production
                samesite='Lax'  # Adjust as needed (e.g., 'Strict' or 'None')
            )
        return response
    

class CookieTokenRefreshView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            access_token = response.data.get('access')

            # Update the access token in the HttpOnly cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Set to True in production
                samesite='Lax'  # Adjust as needed (e.g., 'Strict' or 'None')
            )
        return response