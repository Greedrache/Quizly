from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from auth_app.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    This serializer handles the validation and creation of a new user account.
    It includes fields for username, email, password, and confirmed_password.
    The confirmed_password field is used to ensure that the user correctly confirms their password during registration.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirmed_password', 'email']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        """
        Validate that the confirmed password matches the original password.
        This method checks if the 'confirmed_password' field matches the 'password' field in
        the initial data. If they do not match, it raises a ValidationError."""
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        """
        Validate that the email is unique in the system.
        This method checks if a user with the given email already exists in the database.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        """
        Create and save a new user instance with the provided validated data.
        This method extracts the password and email from the validated data, creates a new User instance, 
        sets the password using Django's set_password method (which hashes the password), and saves the user to the database.
        """
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account
    



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to include user details in the token response.
    This serializer extends the default TokenObtainPairSerializer to add user information
    to the response when a user logs in.
    It validates the username and password, and if valid, it returns the access and refresh tokens
    along with a success message and user details (id, username, email).
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer and remove the 'email' field if it exists, because we are using 'username' for authentication.
        """
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields.pop('email')

    def validate(self, attrs):
        """
        Validate the username and password, and return tokens along with user details.
        This method checks for unexpected fields in the input data, validates the username and password against the database,
        and if valid, generates JWT tokens and returns them along with a success message and user details.
        """
        allowed = set(self.fields.keys())
        initial_keys = set(self.initial_data.keys())
        extra = initial_keys - allowed
        if extra:
            raise serializers.ValidationError(f'Unexpected fields: {", ".join(sorted(extra))}')

        username = attrs.get('username')
        password = attrs.get('password')

        user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            refresh = self.get_token(user)

            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'detail': 'Login successfully!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
        raise AuthenticationFailed('Invalid username or password')