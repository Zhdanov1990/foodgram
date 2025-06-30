from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework import serializers

User = get_user_model()


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['current_password']):
            raise serializers.ValidationError({
                'current_password': 'Неверный текущий пароль'
            })
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
