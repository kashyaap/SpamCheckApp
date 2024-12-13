from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from ...models import User
from ...Serializers.user import UserSerializer

class UserRegistrationAPIView(APIView):
    """
    API endpoint for user registration.
    """

    def post(self, request):
        # Extract and copy request data to make it mutable
        data = request.data.copy()
        
        # Check if the phone number exists
        phone_number = data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"error": "A user with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Encrypt the password
        data['password'] = make_password(data.get('password'))
        
        # Pass the data to the serializer
        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        else:
            errors = self.format_serializer_errors(serializer.errors)
            return Response(
                {"error": "Validation failed.", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def format_serializer_errors(self, errors):
        """
        Custom method to format error messages from serializer.
        
        Args:
            errors (dict): Serializer errors.
        
        Returns:
            dict: Custom error messages for each field.
        """
        formatted_errors = {}
        for field, error_list in errors.items():
            formatted_errors[field] = error_list[0]  # Return only the first error message for each field
        return formatted_errors
