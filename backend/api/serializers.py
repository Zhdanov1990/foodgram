import base64

import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from api.constants import (
    ALLOWED_IMAGE_FORMATS, MAX_AMOUNT, MAX_COOKING_TIME,
    MAX_IMAGE_SIZE, MIN_AMOUNT, MIN_COOKING_TIME,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()
ERR_MSG = (
    'Не удается войти в систему '
    'с предоставленными учетными данными.'
)


class TokenSerializer(serializers.Serializer):
    """Email+password, token."""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
    )
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            email=attrs.get('email'),
            password=attrs.get('password'),
        )
        if not user:
            raise serializers.ValidationError(
                ERR_MSG, code='authorization'
            )
        attrs['user'] = user
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Вывод списка пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.following.filter(author=obj).exists()

    def validate_avatar(self, value):
        """Валидация аватара."""
        if not value:
            return value

        # Если это base64 строка
        if isinstance(value, str) and value.startswith('data:image'):
            try:
                fmt, imgstr = value.split(';base64,')
                ext = fmt.split('/')[-1]

                # Проверяем размер
                size = len(base64.b64decode(imgstr))
                if size > MAX_IMAGE_SIZE:
                    raise serializers.ValidationError(
                        'Размер изображения не должен превышать 10MB.'
                    )

                # Проверяем формат
                content_type = f'image/{ext}'
                if content_type not in ALLOWED_IMAGE_FORMATS:
                    raise serializers.ValidationError(
                        'Поддерживаются форматы: JPEG, PNG, GIF.'
                    )

                # Создаем файл
                avatar_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'avatar.{ext}'
                )
                return avatar_file

            except Exception as e:
                raise serializers.ValidationError(
                    f'Ошибка обработки изображения: {str(e)}'
                )

        # Если это обычный файл
        if hasattr(value, 'size'):
            if value.size > MAX_IMAGE_SIZE:
                raise serializers.ValidationError(
                    'Размер изображения не должен превышать 10MB.'
                )

            if hasattr(value, 'content_type'):
                if value.content_type not in ALLOWED_IMAGE_FORMATS:
                    raise serializers.ValidationError(
                        'Поддерживаются форматы: JPEG, PNG, GIF.'
                    )

        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Создание пользователя."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'avatar', 'password',
        )
        extra_kwargs = {
            'avatar': {'required': False},
            'password': {'write_only': True},
        }

    def validate_password(self, password):
        validators.validate_password(password)
        return password

    def create(self, validated_data):
        pwd = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(pwd)
        user.save()
        return user


class IngredientWriteSerializer(serializers.Serializer):
    """Добавление ингредиента в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        ]
    )


class TagSerializer(serializers.ModelSerializer):
    """Тег."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиент."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиент в рецепте (чтение)."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name',
            'measurement_unit', 'amount',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создание/обновление рецепта."""
    image = Base64ImageField(use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientWriteSerializer(
        many=True,
        write_only=True,
    )
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME),
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'image',
            'cooking_time', 'tags', 'ingredients',
        )
        read_only_fields = ('id',)

    def validate_image(self, value):
        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError(
                'Размер изображения не должен превышать 10MB.'
            )
        ct = getattr(value, 'content_type', None)
        if ct and ct not in ALLOWED_IMAGE_FORMATS:
            raise serializers.ValidationError(
                'Поддерживаются форматы: JPEG, PNG, GIF.'
            )
        return value

    def validate(self, data):
        ing = data.get('ingredients', [])
        if not ing:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        ids = [item['id'].id for item in ing]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиент должен быть уникальным!'
            )
        return data

    def _bulk_create_ingredients(self, recipe, ingredients):
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ing = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user,
        )
        recipe.tags.set(tags)
        self._bulk_create_ingredients(recipe, ing)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ing = validated_data.pop('ingredients')
            instance.recipeingredient_set.all().delete()
            self._bulk_create_ingredients(instance, ing)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта."""
    author = UserListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.in_favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.in_shopping_carts.filter(user=user).exists()
        )


class UserWithRecipesSerializer(serializers.ModelSerializer):
    """Пользователь + рецепты."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'avatar',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.following.filter(author=obj).exists()

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        qs = obj.recipes.all()
        if limit:
            qs = qs[:int(limit)]
        from api.serializers import RecipeMinifiedSerializer
        return RecipeMinifiedSerializer(
            qs, many=True, context=self.context
        ).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Краткий рецепт."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Данные автора в подписке."""
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count', read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        qs = obj.author.recipes.all()
        if limit:
            qs = qs[:int(limit)]
        from api.serializers import RecipeReadSerializer
        return RecipeReadSerializer(
            qs, many=True, context=self.context
        ).data
