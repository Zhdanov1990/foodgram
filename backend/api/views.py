from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser import permissions as djoser_perms
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    TagSerializer, UserCreateSerializer, UserListSerializer,
    UserWithRecipesSerializer,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription
from users.serializers import UserSetPasswordSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        return qs


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action in (
            'list', 'retrieve', 'favorites',
            'download_shopping_cart', 'get_link'
        ):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self, 'filterset_class'):
            self.filterset = self.filterset_class(
                self.request.GET,
                queryset=qs,
                request=self.request
            )
            qs = self.filterset.qs
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _handle_relation(self, request, relation, name):
        recipe = self.get_object()
        exists = relation.filter(recipe=recipe).exists()
        if request.method == 'POST':
            if exists:
                return Response(
                    {'errors': f'Рецепт уже в {name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            relation.create(recipe=recipe)
            return Response(
                RecipeReadSerializer(
                    recipe,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        if not exists:
            return Response(
                {'errors': f'Рецепт не найден в {name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        relation.filter(recipe=recipe).delete()
        return Response(
            RecipeReadSerializer(
                recipe,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self._handle_relation(
            request,
            request.user.favorites,
            'избранном'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_relation(
            request,
            request.user.shopping_cart,
            'корзине'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        """Подписка на автора рецепта."""
        recipe = self.get_object()
        author = recipe.author
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.user.following.filter(author=author).exists():
                return Response(
                    {'errors': 'Уже подписаны на автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                user=request.user,
                author=author
            )
            data = UserWithRecipesSerializer(
                author,
                context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)

        # DELETE
        subscription = get_object_or_404(
            Subscription,
            user=request.user,
            author=author
        )
        subscription.delete()
        data = UserWithRecipesSerializer(
            author,
            context={'request': request}
        ).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        qs = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=request.user
        )
        ingredients = qs.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount')).order_by(
            'ingredient__name'
        )
        lines = [
            f"{i['ingredient__name']} — "
            f"{i['total']} {i['ingredient__measurement_unit']}"
            for i in ingredients
        ]
        resp = HttpResponse('\n'.join(lines), content_type='text/plain')
        resp['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return resp

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        return Response({
            'link': request.build_absolute_uri(
                recipe.get_absolute_url()
            )
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorites(self, request):
        favs = Recipe.objects.filter(
            in_favorites__user=request.user
        ).order_by('-pub_date')
        if hasattr(self, 'filterset_class'):
            self.filterset = self.filterset_class(
                request.GET,
                queryset=favs,
                request=request
            )
            favs = self.filterset.qs
        page = self.paginate_queryset(favs)
        serializer = RecipeReadSerializer(
            page or favs,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UserViewSet(DjoserUserViewSet):
    """Пользователи и подписки."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    pagination_class = CustomPagination
    permission_classes = [
        djoser_perms.CurrentUserOrAdminOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписка через профиль пользователя."""
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user.following.filter(author=author).exists():
                return Response(
                    {'errors': 'Уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            data = UserWithRecipesSerializer(
                author,
                context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)

        # DELETE
        subscription = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        subscription.delete()
        data = UserWithRecipesSerializer(
            author,
            context={'request': request}
        ).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        authors = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(
            page or authors,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['post', 'put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновление аватара пользователя."""
        user = request.user

        if request.method in ['POST', 'PUT']:
            serializer = UserListSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # DELETE - удаление аватара
        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get', 'put', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(self.get_serializer(request.user).data)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request):
        s = UserSetPasswordSerializer(
            request.user,
            data=request.data,
            context={'request': request},
        )
        s.is_valid(raise_exception=True)
        s.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.AllowAny]
    )
    def activation(self, request):
        return Response(
            {'detail': 'Активация не требуется'},
            status=status.HTTP_200_OK
        )
