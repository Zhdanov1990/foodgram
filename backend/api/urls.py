# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    TagViewSet, IngredientViewSet,
    RecipeViewSet, UserViewSet
)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
