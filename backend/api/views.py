from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from djoser import permissions as djoser_permissions
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserWithRecipesSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)
from users.models import Subscription
from users.serializers import UserSetPasswordSerializer

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
        qs = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        return qs


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['name']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in [
            'list', 'retrieve', 'favorites',
            'download_shopping_cart', 'get_link'
        ]:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        qs = Recipe.objects.all().order_by('-pub_date')
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

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self._handle_favorite_shopping_cart(
            request, pk, Favorite, 'favorite'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_favorite_shopping_cart(
            request, pk, ShoppingCart, 'shopping_cart'
        )

    def _handle_favorite_shopping_cart(self, request, pk, model, action_name):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Рецепт уже добавлен в {action_name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeReadSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = get_object_or_404(model, user=user, recipe=recipe)
            obj.delete()
            serializer = RecipeReadSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                f"{ingredient['ingredient__name']} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['ingredient__measurement_unit']}"
            )

        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return Response({
            'link': request.build_absolute_uri(recipe.get_absolute_url())
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorites(self, request):
        user = request.user
        favs = Recipe.objects.filter(
            in_favorites__user=user
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
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [djoser_permissions.CurrentUserOrAdminOrReadOnly]
    pagination_class = CustomPagination

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
        user = request.user
        author = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            serializer = UserWithRecipesSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscription.delete()
            serializer = UserWithRecipesSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserWithRecipesSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post', 'put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method in ['POST', 'PUT']:
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
                user.save()
                data = UserListSerializer(
                    user, context={'request': request}
                ).data
                return Response(data, status=status.HTTP_200_OK)
            if request.data.get('avatar'):
                try:
                    import base64
                    from django.core.files.base import ContentFile
                    avatar_data = request.data['avatar']
                    if avatar_data.startswith('data:image'):
                        fmt, imgstr = avatar_data.split(';base64,')
                        ext = fmt.split('/')[-1]
                        size = len(base64.b64decode(imgstr))
                        if size > 10 * 1024 * 1024:
                            return Response(
                                {'detail': 'Макс. размер 10MB'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        avatar_file = ContentFile(
                            base64.b64decode(imgstr),
                            name=f'avatar.{ext}'
                        )
                        user.avatar = avatar_file
                        user.save()
                        data = UserListSerializer(
                            user, context={'request': request}
                        ).data
                        return Response(data)
                    return Response(
                        {'detail': 'Неверный формат'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except Exception as e:
                    return Response(
                        {'detail': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {'detail': 'Файл не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
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
        serializer = UserSetPasswordSerializer(
            request.user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
