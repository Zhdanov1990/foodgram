from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    SubscriptionSerializer, TagSerializer, UserListSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscription

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None
    
    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = [IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['name']

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('-pub_date')
        # Передаем request в фильтр
        if hasattr(self, 'filterset_class'):
            self.filterset = self.filterset_class(
                self.request.GET,
                queryset=queryset,
                request=self.request
            )
            queryset = self.filterset.qs
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'detail': 'Уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeReadSerializer(
                    recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'detail': 'Уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeReadSerializer(
                    recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        qs = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(total=Sum('amount'))
        lines = [
            f"{item['name']} ({item['unit']}) — {item['total']}"
            for item in qs
        ]
        content = "\n".join(lines)
        response = Response(
            content,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny]
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        # Возвращаем URL рецепта
        from django.urls import reverse
        from django.contrib.sites.shortcuts import get_current_site
        current_site = get_current_site(request)
        recipe_url = f"https://{current_site.domain}/recipes/{recipe.id}/"
        return Response({'url': recipe_url})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'detail': 'Уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            sub = Subscription.objects.create(user=user, author=author)
            return Response(
                SubscriptionSerializer(
                    sub,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        Subscription.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        subs = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subs)
        serializer = SubscriptionSerializer(
            page or subs,
            many=True,
            context={'request': request}
        )
        return (
            self.get_paginated_response(serializer.data)
            if page else Response(serializer.data)
        )

    @action(
        detail=False,
        methods=['post', 'put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method in ['POST', 'PUT']:
            # Проверяем, есть ли файл в запросе
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
                user.save()
                return Response(
                    UserListSerializer(user, context={'request': request}).data,
                    status=status.HTTP_200_OK
                )
            # Проверяем, есть ли данные в JSON (base64)
            elif request.data and 'avatar' in request.data:
                try:
                    import base64
                    from django.core.files.base import ContentFile
                    
                    # Извлекаем base64 данные
                    avatar_data = request.data['avatar']
                    if avatar_data.startswith('data:image'):
                        # Убираем префикс data:image/...;base64,
                        format, imgstr = avatar_data.split(';base64,')
                        ext = format.split('/')[-1]
                        
                        # Создаем файл из base64
                        avatar_file = ContentFile(base64.b64decode(imgstr), name=f'avatar.{ext}')
                        user.avatar = avatar_file
                        user.save()
                        
                        return Response(
                            UserListSerializer(user, context={'request': request}).data,
                            status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {'detail': 'Неверный формат изображения'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Exception as e:
                    return Response(
                        {'detail': f'Ошибка обработки изображения: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'detail': 'Файл аватара не найден.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
