from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', include('djoser.urls')),
    # Кастомные URL для подписок и аватаров
    path('users/<int:pk>/subscribe/', UserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'}), name='user-subscribe'),
    path('users/subscriptions/', UserViewSet.as_view({'get': 'subscriptions'}), name='user-subscriptions'),
    path('users/me/avatar/', UserViewSet.as_view({'post': 'avatar', 'put': 'avatar', 'delete': 'avatar'}), name='user-avatar'),
    # URL для избранных рецептов
    path('recipes/favorites/', RecipeViewSet.as_view({'get': 'favorites'}), name='recipe-favorites'),
]
