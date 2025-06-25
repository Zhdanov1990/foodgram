from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(name__istartswith=value)


class RecipeFilter(filters.FilterSet):
    tags = filters.BaseInFilter(
        field_name='tags__slug',
        method='filter_tags'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_shopping_carts__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        print("=== FILTER_TAGS CALLED ===")
        print(f"Filter tags called with value: {value}")
        print(f"Value type: {type(value)}")
        if value:
            print(f"Filtering by tags: {value}")
            return queryset.filter(tags__slug__in=value).distinct()
        return queryset

    def __init__(self, *args, **kwargs):
        print("=== RECIPE_FILTER INIT ===")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")
        super().__init__(*args, **kwargs)
        print("=== RECIPE_FILTER INIT COMPLETE ===")
