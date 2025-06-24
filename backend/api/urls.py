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
router.register('users', UserViewSet, basename='users')

urlpatterns = [

    path(
        'recipes/favorites/',
        RecipeViewSet.as_view({'get': 'favorites'}),
        name='recipe-favorites'
    ),
    path(
        'users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
        name='user-subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/',
        UserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'}),
        name='user-subscribe'
    ),
    path(
        'users/me/avatar/',
        UserViewSet.as_view({
            'post': 'avatar',
            'put': 'avatar',
            'delete': 'avatar'
        }),
        name='user-avatar'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
