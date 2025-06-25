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
    tags = filters.AllValuesMultipleFilter(
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

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        
        # Получаем все доступные теги
        all_tags = list(Recipe.objects.values_list('tags__slug', flat=True).distinct())
        all_tags = [tag for tag in all_tags if tag is not None]
        
        # Если выбраны ВСЕ теги - показываем ВСЕ рецепты
        if set(value) == set(all_tags):
            return queryset
        
        # Иначе фильтруем по выбранным тегам
        return queryset.filter(tags__slug__in=value).distinct()

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_shopping_carts__user=self.request.user)
        return queryset
