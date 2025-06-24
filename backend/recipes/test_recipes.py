import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import User


@pytest.mark.django_db
def test_tag_creation():
    tag = Tag.objects.create(
        name="Тест",
        color="#FFFFFF",
        slug="test"
    )
    assert tag.name == "Тест"
    assert tag.color == "#FFFFFF"
    assert tag.slug == "test"


@pytest.mark.django_db
def test_ingredient_creation():
    ingr = Ingredient.objects.create(
        name="Картофель",
        measurement_unit="г"
    )
    assert ingr.name == "Картофель"
    assert ingr.measurement_unit == "г"


@pytest.mark.django_db
def test_recipe_creation():
    user = User.objects.create_user(
        username="testuser",
        password="testpass"
    )
    ingr = Ingredient.objects.create(
        name="Морковь",
        measurement_unit="г"
    )
    tag = Tag.objects.create(
        name="Обед",
        color="#49B64E",
        slug="lunch"
    )
    recipe = Recipe.objects.create(
        author=user,
        name="Тестовый рецепт",
        image="recipes/test.jpg",
        text="Описание",
        cooking_time=10
    )
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingr,
        amount=100
    )
    recipe.tags.add(tag)
    assert recipe.name == "Тестовый рецепт"
    assert recipe.author == user
    assert ingr in recipe.ingredients.all()
    assert tag in recipe.tags.all()


@pytest.mark.django_db
def test_recipe_str():
    recipe = Recipe(name="Тестовый рецепт")
    assert str(recipe) == "Тестовый рецепт"


@pytest.mark.django_db
def test_ingredient_str():
    ingredient = Ingredient(
        name="Сахар",
        measurement_unit="г"
    )
    assert str(ingredient) == "Сахар (г)"


@pytest.mark.django_db
def test_recipe_list_api():
    client = APIClient()
    url = reverse("recipes-list")
    response = client.get(url)
    assert response.status_code == 200
