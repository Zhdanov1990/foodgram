# backend/api/views.py

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser import permissions as djoser_permissions

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserListSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
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
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            data = RecipeReadSerializer(
                recipe, context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
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
            if ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            data = RecipeReadSerializer(
                recipe, context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
        ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).delete()
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
            f"{item['name']} — {item['total']} {item['unit']}"
            for item in qs
        ]
        content = "\n".join(lines)
        resp = HttpResponse(content, content_type='text/plain')
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
        recipe = get_object_or_404(Recipe, pk=pk)
        from django.conf import settings

        domain = getattr(settings, 'DOMAIN_NAME', 'localhost')
        recipe_url = f"https://{domain}/recipes/{recipe.id}/"

        return Response({'url': recipe_url})


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
        page = self.paginate_queryset(favs)
        serializer = RecipeReadSerializer(
            page or favs,
            many=True,
            context={'request': request}
        )
        if page:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [djoser_permissions.CurrentUserOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'me':
            return UserListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

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
                    {'detail': 'Нельзя подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=user, author=author
            ).exists():
                return Response(
                    {'detail': 'Уже подписаны.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            sub = Subscription.objects.create(
                user=user, author=author
            )
            data = SubscriptionSerializer(
                sub, context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
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
        if page:
            return self.get_paginated_response(serializer.data)
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
        permission_classes=[permissions.AllowAny]
    )
    def activation(self, request):
        return Response(
            {'detail': 'Активация не требуется'},
            status=status.HTTP_200_OK
        )
