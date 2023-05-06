"""
Serializers for user API View.
"""
from rest_framework import serializers
from django.contrib.auth import (get_user_model,
                                 authenticate)
from django.utils.translation import gettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'name', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        """create and return user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user  with encrypted password."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={
        'input_type': 'password'
    },
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate user."""
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }

        user = authenticate(request=self.context.get('request'),
                            **credentials)
        if not user:
            msg = _('Unable to authenticate with given credentials.')
            raise serializers.ValidationError(msg, code='Authenticate')
        attrs['user'] = user
        return attrs

