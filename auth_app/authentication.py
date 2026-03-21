from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that extends JWTAuthentication to support token retrieval from HttpOnly cookies.
    This class overrides the authenticate method to first check for the presence of the JWT token in the Authorization header, and if not found, it looks for the token in the 'access_token' cookie.
    This allows the application to support authentication via cookies, which can be more secure against certain types of attacks (e.g., XSS) since HttpOnly cookies cannot be accessed via JavaScript.
    If a valid token is found in either the header or the cookie, the user is authenticated and returned. If the token is invalid or expired, an AuthenticationFailed exception is raised.
    """
    def authenticate(self, request):
        header = self.get_header(request)
        
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get('access_token')
            
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken:
            raise AuthenticationFailed('Token ist ungültig oder abgelaufen')

        return self.get_user(validated_token), validated_token
