import django.contrib.auth.password_validation as validators

from django.contrib.auth import authenticate, get_user_model
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
ERR_MSG = 'Не удается войти в систему с предоставленными учетными данными.'


class TokenSerializer(serializers.Serializer):
    """Логин через email+password → получение токена."""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
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
                ERR_MSG,
                code='authorization'
            )
        attrs['user'] = user
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка пользователей."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed'
        )

    def validate_avatar(self, value):
        if value:
            # Проверяем размер файла
            if value.size > MAX_IMAGE_SIZE:
                raise serializers.ValidationError(
                    'Размер изображения не должен превышать 10MB.'
                )
            # Проверяем формат файла
            if (
                hasattr(value, 'content_type')
                and value.content_type not in ALLOWED_IMAGE_FORMATS
            ):
                raise serializers.ValidationError(
                    'Поддерживаются только форматы: JPEG, PNG, GIF.'
                )
        return value

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.following.filter(author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False}
        }

    def validate_password(self, password):
        validators.validate_password(password)
        return password

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


def _validate_unique_ingredients(ingredients):
    """Проверяет уникальность ингредиентов в рецепте."""
    seen = set()
    for item in ingredients:
        iid = item['id']
        if iid in seen:
            raise serializers.ValidationError(
                'Ингредиент должен быть уникальным!'
            )
        seen.add(iid)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientWriteSerializer(serializers.Serializer):
    """Сериализатор для добавления ингредиента в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        ]
    )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""
    image = Base64ImageField(use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientWriteSerializer(many=True, write_only=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'image',
            'cooking_time', 'tags', 'ingredients'
        )
        read_only_fields = ('id',)

    def validate_image(self, value):
        if value:
            # Проверяем размер файла
            if value.size > MAX_IMAGE_SIZE:
                raise serializers.ValidationError(
                    'Размер изображения не должен превышать 10MB.'
                )
            # Проверяем формат файла
            if (
                hasattr(value, 'content_type')
                and value.content_type not in ALLOWED_IMAGE_FORMATS
            ):
                raise serializers.ValidationError(
                    'Поддерживаются только форматы: JPEG, PNG, GIF.'
                )
        return value

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        _validate_unique_ingredients(ingredients)
        return data

    def _bulk_create_ingredients(self, recipe, ingredients):
        """Создает ингредиенты рецепта используя bulk_create."""
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._bulk_create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            self._bulk_create_ingredients(
                instance,
                validated_data.pop('ingredients')
            )
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""
    author = UserListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True
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
            and user.favorites.filter(
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(
                recipe=obj
            ).exists()
        )


class UserWithRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с рецептами в подписках."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.following.filter(author=obj).exists()

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit', 3)
        qs = obj.recipes.all()
        if limit:
            qs = qs[:int(limit)]
        return RecipeMinifiedSerializer(
            qs,
            many=True,
            context=self.context
        ).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Выдача информации об авторе и его рецептах при подписке."""
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count',
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        qs = obj.author.recipes.all()
        if limit:
            qs = qs[:int(limit)]
        return RecipeReadSerializer(
            qs,
            many=True,
            context=self.context
        ).data
