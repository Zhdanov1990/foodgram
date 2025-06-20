from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        # Djoser передает email как именованный аргумент,
        # поэтому получаем его из kwargs.
        # Для совместимости также проверяем и username.
        email = kwargs.get('email', username)
        if not email:
            return None
            
        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None 