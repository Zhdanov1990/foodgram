import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

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

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'password'
        )

    def validate_password(self, password):
        validators.validate_password(password)
        return make_password(password)


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
    ingredients = serializers.ListSerializer(
        child=serializers.DictField(),
        write_only=True
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
            print(f"DEBUG: Validating image - size: {getattr(value, 'size', 'unknown')}, type: {getattr(value, 'content_type', 'unknown')}")
            
            # Проверяем размер файла (10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(
                    'Размер изображения не должен превышать 10MB.'
                )
            
            # Проверяем формат файла
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(value, 'content_type') and value.content_type not in allowed_formats:
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

    def create(self, validated_data):
        print(f"DEBUG: Creating recipe with data: {validated_data.keys()}")
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        # Убираем author из validated_data, если он там есть
        validated_data.pop('author', None)
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        recipe.tags.set(tags)
        for item in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
        print(f"DEBUG: Recipe created successfully with ID: {recipe.id}")
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            for item in validated_data.pop('ingredients'):
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=item['id'],
                    amount=item['amount']
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
            user.is_authenticated and
            obj.in_favorites.filter(pk=user.pk).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            obj.in_shopping_carts.filter(pk=user.pk).exists()
        )


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
