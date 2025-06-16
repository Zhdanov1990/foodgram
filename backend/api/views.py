# backend/api/views.py

from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (
    Recipe, Tag, Ingredient, RecipeIngredient,
    Favorite, ShoppingCart
)
from users.models import Subscription
from api.serializers import (
    TagSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeWriteSerializer,
    UserListSerializer, SubscriptionSerializer
)
from api.permissions import IsAuthorOrAdminOrReadOnly, IsAdminOrReadOnly

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['^name']
    filterset_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = [IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tags', 'author']
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Уже в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeReadSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Уже в списке покупок.'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeReadSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        qs = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(total=Sum('amount'))
        lines = [f"{item['name']} ({item['unit']}) — {item['total']}" for item in qs]
        content = "\n".join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        if request.method == 'POST':
            if user == author or Subscription.objects.filter(user=user, author=author).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            sub = Subscription.objects.create(user=user, author=author)
            return Response(
                SubscriptionSerializer(sub, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        Subscription.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        subs = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subs)
        serializer = SubscriptionSerializer(page or subs, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)
