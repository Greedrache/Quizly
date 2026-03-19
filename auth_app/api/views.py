from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            # Set the access token in an HttpOnly cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Set to True in production
                samesite='Lax'  # Adjust as needed (e.g., 'Strict' or 'None')
            )
            
            # Set the refresh token in an HttpOnly cookie
            if refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    secure=True,  # Set to True in production
                    samesite='Lax'  # Adjust as needed
                )
            
            # Remove tokens from the JSON response to only return detail and user
            response.data.pop('access', None)
            response.data.pop('refresh', None)
        return response
    

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Extract the refresh token from the HttpOnly cookie
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is missing from cookies."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Inject it into the request data so the SimpleJWT serializer can process it
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data['refresh'] = refresh_token

        # Get the standard SimpleJWT serializer (TokenRefreshSerializer)
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        # Extract newly minted access token (and refresh token, if rotation is enabled)
        access_token = serializer.validated_data.get('access')
        refresh_token_new = serializer.validated_data.get('refresh')

        # Since we just want the 'detail' string in our response body:
        response = Response({'detail': 'Token refreshed'}, status=status.HTTP_200_OK)

        # Set the newly generated access token in the cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        # If refresh token rotation is enabled, simplejwt will give us a new refresh token
        if refresh_token_new:
            response.set_cookie(
                key='refresh_token',
                value=refresh_token_new,
                httponly=True,
                secure=True,
                samesite='Lax'
            )

        return response

class LogoutView(APIView):
    '''
    Logout by deleting the access and refresh tokens from the cookies.
    Note: This does not invalidate the tokens server-side :), so they could still be used until
    they expire. For true logout, consider implementing token blacklisting.
    '''
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response