from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...models import User
from ...Serializers.user import UserSerializer

class UserProfileAPIView(APIView):
    """
    API endpoint for managing user profiles.

    Methods:
        get(request): Fetches the logged-in user's profile.
        patch(request): Updates the logged-in user's profile.

    Returns:
        Response: JSON response containing profile data or update confirmation.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch the logged-in user's profile.
        """
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update the logged-in user's profile.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )

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
            formatted_errors[field] = error_list[0]  #
