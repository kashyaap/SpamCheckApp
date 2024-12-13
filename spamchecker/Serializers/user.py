from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = [
            'id', 'salutation', 'first_name', 'last_name', 'occupation',
            'phone_number', 'country_code', 'email', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'first_name': {'error_messages': {'required': 'First name is required.'}},
            'last_name': {'error_messages': {'required': 'Last name is required.'}},
            'country_code': {'error_messages': {'required': 'Country code is required.'}},
            'phone_number': {'error_messages': {'required': 'Phone number is required.'}},
            'email': {'error_messages': {'required': 'Email is required.', 'invalid': 'Enter a valid email address.'}},
        }

    def validate_phone_number(self, value):
        """
        Custom validation logic for phone_number.
        """
        if not value.isdigit():
            raise serializers.ValidationError('Phone number must be numeric.')
        return value

    def validate_email(self, value):
        """
        Custom validation logic for email.
        """
        if '@example.com' in value:
            raise serializers.ValidationError('Email addresses from example.com are not allowed.')
        return value
