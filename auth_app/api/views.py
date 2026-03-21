from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



class RegistrationView(APIView):
    """
    API endpoint for user registration.
    This view allows new users to create an account by providing a username, email, password,
    and repeated password for confirmation. It uses the RegistrationSerializer to validate the input data and create a new user.
    The view is accessible to anyone (AllowAny permission) since it's meant for new users who don't have an account yet.
    """    
    permission_classes = [AllowAny]


    def post(self, request):
        """
        Handle POST requests to register a new user.
        This method takes the incoming request data, validates it using the RegistrationSerializer, and if valid
        creates a new user account. It returns a success message upon successful registration or error details if the input data is invalid.
        """
        serializer = RegistrationSerializer(data=request.data) 

        if serializer.is_valid():
            saved_account = serializer.save()
            return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens and setting them in HttpOnly cookies.
    This view extends the default TokenObtainPairView to include functionality for setting the access and
    refresh tokens in HttpOnly cookies upon successful login. It uses the CustomTokenObtainPairSerializer to include user details in the response.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to log in a user and set JWT tokens in cookies.
        This method processes the login request, validates the credentials, and if valid, generates JWT tokens
        and sets them in HttpOnly cookies. It also removes the tokens from the JSON response to only return user details and a success message.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,  # Set to True in production to only allow cookies over HTTPS
                samesite='Lax'  # Is for CSRF protection, adjust as needed (e.g. 'Strict' or 'None' if you need cross-site cookies)
            )
            
            if refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    secure=False,  # Set to True in production to only allow cookies over HTTPS
                    samesite='Lax'  # Is for CSRF protection, adjust as needed (e.g. 'Strict' or 'None' if you need cross-site cookies)
                )
            
            response.data.pop('access', None)
            response.data.pop('refresh', None)
        return response
    

class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing JWT tokens using the refresh token from HttpOnly cookies.
    This view extends the default TokenRefreshView to read the refresh token from HttpOnly cookies instead
    of the request body. It generates a new access token (and optionally a new refresh token if rotation is enabled) and sets them in cookies.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is missing from cookies."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data['refresh'] = refresh_token

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get('access')
        refresh_token_new = serializer.validated_data.get('refresh')

        response = Response({'detail': 'Token refreshed'}, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax'
        )

        if refresh_token_new:
            response.set_cookie(
                key='refresh_token',
                value=refresh_token_new,
                httponly=True,
                secure=False,
                samesite='Lax'
            )

        return response

class LogoutView(APIView):
    """
    Logout by deleting the access and refresh tokens from the cookies.
    Note: This does not invalidate the tokens server-side :), so they could still be used until
    they expire. For true logout, consider implementing token blacklisting.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests to log out a user by clearing JWT tokens from cookies.
        This method creates a response indicating successful logout and deletes the 'access_token' and 'refresh_token' cookies to effectively log the user out on the client side. 
        Note that this does not invalidate the tokens server-side, so they could still be used until they expire. For true logout, consider implementing token blacklisting.
        """
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response